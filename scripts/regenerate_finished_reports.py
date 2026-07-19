"""Regenerate complete reports for finished corpora using 5-system scoring.

Uses publication.predict_systems (Baseline, Majority, Legacy escalation,
Evidence-weighted raw, Evidence-weighted structured) offline from saved runs.
Does not call Ollama.
"""

from __future__ import annotations

import json
import math
import time
from collections import Counter
from pathlib import Path

from quorum.publication import SYSTEMS, predict_systems

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAIRS = ROOT / "data" / "pairs"


def _metrics(rows: list[dict], key: str) -> dict:
    tp = fp = tn = fn = esc = err = 0
    for r in rows:
        t = r["truth"]
        p = r["predictions"].get(key)
        if p == "escalate":
            esc += 1
            continue
        if p not in ("conflict", "no_conflict"):
            err += 1
            continue
        if t == "conflict" and p == "conflict":
            tp += 1
        elif t == "no_conflict" and p == "conflict":
            fp += 1
        elif t == "no_conflict" and p == "no_conflict":
            tn += 1
        elif t == "conflict" and p == "no_conflict":
            fn += 1
    n = len(rows)
    decided = tp + fp + tn + fn
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    spec = tn / (tn + fp) if (tn + fp) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    bal = 0.5 * (rec + spec)
    denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = ((tp * tn) - (fp * fn)) / denom if denom else 0.0
    return {
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "escalate": esc,
        "error": err,
        "accuracy": (tp + tn) / n if n else 0.0,
        "precision": prec,
        "recall": rec,
        "specificity": spec,
        "f1": f1,
        "balanced_accuracy": bal,
        "mcc": mcc,
        "coverage": decided / n if n else 0.0,
        "escalation_rate": esc / n if n else 0.0,
    }


def score_corpus(
    name: str,
    raw_path: Path,
    structured_path: Path | None = None,
    pairs_root: Path = PAIRS,
) -> dict:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    raw_by = {r["pair"]: r for r in raw["results"]}
    struct_by = {}
    if structured_path and structured_path.exists():
        struct = json.loads(structured_path.read_text(encoding="utf-8"))
        struct_by = {r["pair"]: r for r in struct["results"]}

    scored = []
    for pair, raw_row in raw_by.items():
        srow = struct_by.get(pair)
        pred = predict_systems(raw_row, srow, pairs_root)
        scored.append(
            {
                "pair": pair,
                "truth": pred["details"]["truth"],
                "predictions": {
                    k: pred["predictions"][k] for k, _ in SYSTEMS if k in pred["predictions"]
                },
            }
        )

    systems = {k: _metrics(scored, k) for k, _ in SYSTEMS}
    payload = {
        "corpus": name,
        "raw_run": raw_path.name,
        "structured_run": structured_path.name if structured_path else None,
        "n": len(scored),
        "labels": dict(Counter(r["truth"] for r in scored)),
        "systems": systems,
    }

    md = [
        f"# Five-system report — {name}",
        "",
        f"- Raw: `{raw_path.name}`",
        f"- Structured: `{structured_path.name if structured_path else 'n/a'}`",
        f"- N={len(scored)} · labels={payload['labels']}",
        f"- Offline re-adjudication via `publication.predict_systems`",
        "",
        "| System | Acc | Prec | Recall | Spec | F1 | BalAcc | MCC | Cov | Esc |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key, label in SYSTEMS:
        m = systems[key]
        md.append(
            f"| {label} | {m['accuracy']:.1%} | {m['precision']:.1%} | {m['recall']:.1%} | "
            f"{m['specificity']:.1%} | {m['f1']:.1%} | {m['balanced_accuracy']:.1%} | "
            f"{m['mcc']:.2f} | {m['coverage']:.1%} | {m['escalation_rate']:.1%} |"
        )
    md.append("")
    (RESULTS / f"report5_{name}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (RESULTS / f"report5_{name}.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(f"[report5] {name} N={len(scored)}")
    return payload


def main() -> None:
    corpora = [
        (
            "cooperbench_python",
            RESULTS / "run_20260718T182612Z_cooper_raw.json",
            RESULTS / "run_20260718T182612Z_cooper_structured.json",
        ),
        (
            "hard_negatives",
            RESULTS / "run_20260718T224427Z.json",
            RESULTS / "run_hard_negatives_structured_final.json",
        ),
    ]
    parts = []
    for name, raw, struct in corpora:
        if raw.exists():
            parts.append(score_corpus(name, raw, struct if struct.exists() else None))

    # Combined
    md = [
        "# Complete Five-System Evaluation Report",
        "",
        f"Generated: {time.strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "Offline scoring of saved live runs. Live blind_eval / hard_compatible",
        "evals continue in the background and will be appended when finished.",
        "",
    ]
    for p in parts:
        md.append(f"## {p['corpus']} (N={p['n']})")
        md.append("")
        md.append(f"Labels: `{p['labels']}`")
        md.append("")
        md.append("| System | Acc | Prec | Recall | Spec | F1 | BalAcc | MCC | Esc |")
        md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
        for key, label in SYSTEMS:
            m = p["systems"][key]
            md.append(
                f"| {label} | {m['accuracy']:.1%} | {m['precision']:.1%} | {m['recall']:.1%} | "
                f"{m['specificity']:.1%} | {m['f1']:.1%} | {m['balanced_accuracy']:.1%} | "
                f"{m['mcc']:.2f} | {m['escalation_rate']:.1%} |"
            )
        md.append("")
    (RESULTS / "complete_eval_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (RESULTS / "complete_eval_report.json").write_text(
        json.dumps({"corpora": parts, "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ")}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print("[done] results/complete_eval_report.md")


if __name__ == "__main__":
    main()
