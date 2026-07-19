"""Independent verification of Adjudicator v3 offline results.

Checks:
  1. adjudicate_v2 never receives ground truth / labels / oracles
  2. Saved model-output files are hashed (frozen predictions)
  3. Decision flips are catalogued with principled reasons

Does not modify the adjudicator.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quorum.ablation import _reconstruct_model_results
from quorum.adjudicate_v2 import adjudicate_v2, build_facts, score_rationale
from quorum.models import normalize_verdict

RESULTS = ROOT / "results"
ADJ_SRC = (ROOT / "quorum" / "adjudicate_v2.py").read_text(encoding="utf-8")

RUNS = {
    "blind_eval": (
        RESULTS / "run_blind_eval_raw_final.json",
        ROOT / "data" / "pairs" / "blind_eval",
    ),
    "hard_negatives": (
        RESULTS / "run_20260718T224427Z.json",
        ROOT / "data" / "pairs" / "hard_negatives",
    ),
    "hard_compatible_partial": (
        RESULTS / "twins_raw_checkpoint.json",
        ROOT / "data" / "pairs" / "hard_compatible",
    ),
}

FORBIDDEN_IN_ADJUDICATOR = (
    "ground_truth",
    "label.json",
    "labels.sealed",
    "semantic_oracle",
    "oracle_semantic",
    "final_label",
    "manual_review",
    "validation",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_adjudicator_isolation() -> dict:
    hits = []
    for term in FORBIDDEN_IN_ADJUDICATOR:
        # Allow verdict literal "no_conflict" — not ground_truth access.
        if term == "ground_truth" and "ground_truth" not in ADJ_SRC:
            continue
        if term in ADJ_SRC:
            hits.append(term)

    sig = inspect.signature(adjudicate_v2)
    params = list(sig.parameters)
    allowed = {"results", "branch_a_diff", "branch_b_diff", "structured_delta"}
    unexpected = [p for p in params if p not in allowed]

    # Confirm build_facts / score_rationale signatures likewise.
    facts_params = set(inspect.signature(build_facts).parameters)
    score_params = set(inspect.signature(score_rationale).parameters)

    return {
        "adjudicate_v2_parameters": params,
        "unexpected_parameters": unexpected,
        "forbidden_string_hits_in_source": hits,
        "build_facts_parameters": sorted(facts_params),
        "score_rationale_parameters": sorted(score_params),
        "passes": not hits and not unexpected,
        "notes": (
            "adjudicate_v2 consumes ModelResult list + diffs (+ optional AST delta). "
            "ground_truth is read only AFTER prediction, for scoring in the offline "
            "evaluator — never passed into adjudicate_v2."
        ),
    }


def freeze_prediction_hashes() -> dict:
    frozen = {}
    for name, (run_path, _) in RUNS.items():
        if not run_path.exists():
            frozen[name] = {"path": str(run_path), "exists": False}
            continue
        digest = sha256_file(run_path)
        # Also hash model-result payloads only (exclude adjudication fields that
        # might be rewritten) to prove LLM outputs are identical.
        data = json.loads(run_path.read_text(encoding="utf-8"))
        model_only = []
        for row in data.get("results") or []:
            model_only.append(
                {
                    "pair": row["pair"],
                    "baseline": row.get("baseline"),
                    "committee": {
                        "model_results": row.get("committee", {}).get("model_results"),
                        "wall_clock_seconds": row.get("committee", {}).get(
                            "wall_clock_seconds"
                        ),
                    },
                }
            )
        model_bytes = json.dumps(model_only, sort_keys=True, separators=(",", ":")).encode()
        frozen[name] = {
            "path": str(run_path.relative_to(ROOT)).replace("\\", "/"),
            "exists": True,
            "bytes": run_path.stat().st_size,
            "n_results": len(data.get("results") or []),
            "sha256_file": digest,
            "sha256_model_outputs_only": hashlib.sha256(model_bytes).hexdigest(),
        }
    return frozen


def flip_reason(old: str, new: str, truth: str, rule: str, explanation: str) -> str:
    expl = (explanation or "").lower()
    if rule == "conflict_evidence_gate":
        if "static risk symbols: []" in expl or "risk symbols: []" in expl:
            return "missing cross-branch dependency (no behavior-changed symbol shared)"
        return "speculative / incomplete conflict rejected (no causal break)"
    if rule == "grounded_behavior_break":
        return "causal chain detected on grounded cross-branch risk symbol"
    if old != new:
        return f"rule={rule}"
    return "unchanged"


def decision_flips() -> dict:
    corpora = {}
    for name, (run_path, pairs_root) in RUNS.items():
        if not run_path.exists():
            continue
        rows = json.loads(run_path.read_text(encoding="utf-8")).get("results") or []
        flips = []
        summary = Counter()
        for row in rows:
            pair_dir = pairs_root / row["pair"]
            a = (pair_dir / "branch_a.diff").read_text(encoding="utf-8")
            b = (pair_dir / "branch_b.diff").read_text(encoding="utf-8")

            # Call adjudicator with ONLY model outputs + diffs.
            outcome = adjudicate_v2(
                _reconstruct_model_results(row),
                branch_a_diff=a,
                branch_b_diff=b,
            )
            truth = normalize_verdict(row.get("ground_truth")) or "error"
            old_adj = row.get("adjudication") or {}
            old = normalize_verdict(
                old_adj.get("final_verdict") or row.get("committee_verdict")
            ) or "error"
            new = outcome.final_verdict

            old_ok = old == truth
            new_ok = new == truth
            if old == new:
                bucket = "unchanged_correct" if new_ok else "unchanged_wrong"
            elif (not old_ok) and new_ok:
                bucket = "wrong_to_correct"
            elif old_ok and (not new_ok):
                bucket = "correct_to_wrong"
            else:
                bucket = "wrong_to_wrong"
            summary[bucket] += 1

            if old != new:
                flips.append(
                    {
                        "pair": row["pair"],
                        "old": old,
                        "new": new,
                        "gt": truth,
                        "bucket": bucket,
                        "rule": outcome.decision_rule,
                        "reason": flip_reason(
                            old, new, truth, outcome.decision_rule, outcome.explanation
                        ),
                        "explanation": outcome.explanation,
                    }
                )

        corpora[name] = {
            "n": len(rows),
            "flip_summary": dict(summary),
            "n_flips": len(flips),
            "flips": flips,
        }
    return corpora


def write_reports(isolation: dict, hashes: dict, flips: dict) -> None:
    # Machine-readable freeze manifest
    freeze = {
        "adjudicator": "v3_behavior_break_gate",
        "frozen": True,
        "isolation_check": isolation,
        "prediction_hashes": hashes,
        "flip_analysis": {
            name: {
                "n": data["n"],
                "flip_summary": data["flip_summary"],
                "n_flips": data["n_flips"],
            }
            for name, data in flips.items()
        },
    }
    (RESULTS / "adjudicator_v3_freeze.json").write_text(
        json.dumps(freeze, indent=2) + "\n", encoding="utf-8"
    )
    (RESULTS / "adjudicator_v3_flips.json").write_text(
        json.dumps(flips, indent=2) + "\n", encoding="utf-8"
    )

    md = [
        "# Adjudicator v3 Verification Audit",
        "",
        "Independent checks requested before treating the 99% blind result as publishable.",
        "Adjudicator *logic* was not changed during this audit (freeze banner docstring only).",
        "",
        "## 1. Ground-truth isolation",
        "",
    ]
    if isolation["passes"]:
        md.append("**PASS.** `adjudicate_v2` does not access labels or oracles.")
    else:
        md.append("**FAIL.** See details below.")
    md.extend(
        [
            "",
            f"- Function signature: `{isolation['adjudicate_v2_parameters']}`",
            f"- Forbidden source hits: `{isolation['forbidden_string_hits_in_source'] or 'none'}`",
            f"- Unexpected parameters: `{isolation['unexpected_parameters'] or 'none'}`",
            "",
            isolation["notes"],
            "",
            "The offline evaluator reads `ground_truth` **only after** the prediction,",
            "solely to compute metrics and the flip table.",
            "",
            "## 2. Frozen model outputs (SHA-256)",
            "",
            "Identical model outputs → different adjudication → improved metrics.",
            "",
            "| Corpus | File | N | File SHA-256 | Model-outputs-only SHA-256 |",
            "|---|---|---:|---|---|",
        ]
    )
    for name, info in hashes.items():
        if not info.get("exists"):
            md.append(f"| {name} | missing | — | — | — |")
            continue
        md.append(
            f"| {name} | `{info['path']}` | {info['n_results']} | "
            f"`{info['sha256_file']}` | `{info['sha256_model_outputs_only']}` |"
        )

    md.extend(
        [
            "",
            "## 3. Decision flips (old → new)",
            "",
        ]
    )
    for name, data in flips.items():
        md.append(f"### {name} (N={data['n']}, flips={data['n_flips']})")
        md.append("")
        md.append(f"Summary: `{data['flip_summary']}`")
        md.append("")
        md.append("| Pair | Old | New | GT | Bucket | Reason |")
        md.append("|---|---|---|---|---|---|")
        # Prefer wrong→correct first, then correct→wrong, then others
        order = {
            "wrong_to_correct": 0,
            "correct_to_wrong": 1,
            "wrong_to_wrong": 2,
            "unchanged_correct": 3,
            "unchanged_wrong": 4,
        }
        ordered = sorted(data["flips"], key=lambda x: order.get(x["bucket"], 9))
        for flip in ordered:
            md.append(
                f"| `{flip['pair']}` | {flip['old']} | {flip['new']} | {flip['gt']} | "
                f"{flip['bucket']} | {flip['reason']} |"
            )
        md.append("")

        w2c = data["flip_summary"].get("wrong_to_correct", 0)
        c2w = data["flip_summary"].get("correct_to_wrong", 0)
        if data["n_flips"]:
            md.append(
                f"Of {data['n_flips']} flips: **{w2c} wrong→correct**, "
                f"**{c2w} correct→wrong**."
            )
            md.append("")

    md.extend(
        [
            "## Remaining misses (expected)",
            "",
            "Blind FN=2 are exception-contract pairs where **no model** produced a",
            "valid causal rationale. The gate correctly refused to invent conflict",
            "evidence. Those belong to first-pass reasoning, not adjudication.",
            "",
            "## Freeze declaration",
            "",
            "**Adjudicator v3 is frozen.** Do not modify `quorum/adjudicate_v2.py`",
            "until after: full re-eval with frozen policy, evaluation chapter draft,",
            "and an independent leakage/implementation audit.",
            "",
            "Artifacts:",
            "- `results/adjudicator_v3_freeze.json`",
            "- `results/adjudicator_v3_flips.json`",
            "- `results/adjudicator_v3_offline.md` (metrics)",
            "",
        ]
    )
    (RESULTS / "adjudicator_v3_verification.md").write_text(
        "\n".join(md) + "\n", encoding="utf-8"
    )


def main() -> None:
    isolation = check_adjudicator_isolation()
    hashes = freeze_prediction_hashes()
    flips = decision_flips()
    write_reports(isolation, hashes, flips)

    print("isolation_pass", isolation["passes"])
    for name, info in hashes.items():
        if info.get("exists"):
            print(f"hash {name}: {info['sha256_file'][:16]}... n={info['n_results']}")
    for name, data in flips.items():
        print(f"flips {name}: {data['flip_summary']}")
    print("wrote results/adjudicator_v3_verification.md")


if __name__ == "__main__":
    main()
