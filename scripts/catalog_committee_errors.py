"""Priority-1: catalog every committee mistake on leakage-free / hard corpora.

Corpora:
  - blind_eval raw (200 balanced) — primary
  - hard_negatives raw (100 conflict-only)
  - hard_compatible twins checkpoint (partial, all no_conflict)

Does NOT change Quorum adjudication policy. Diagnostic only.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SEALED = ROOT / "dataset" / "blind_eval" / "labels.sealed.jsonl"
PAIRS_BLIND = ROOT / "data" / "pairs" / "blind_eval"
PAIRS_NEG = ROOT / "data" / "pairs" / "hard_negatives"
PAIRS_TWIN = ROOT / "data" / "pairs" / "hard_compatible"


def norm(v):
    if v is None:
        return None
    v = str(v).strip().lower()
    if v == "conflict":
        return "conflict"
    if v in ("no_conflict", "compatible", "clean_merge", "safe"):
        return "no_conflict"
    if v == "escalate":
        return "escalate"
    return v


def sealed_meta() -> dict[str, dict]:
    meta = {}
    if not SEALED.exists():
        return meta
    for line in SEALED.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        meta[str(r["pair_id"])] = {
            "family": r.get("family"),
            "kind": r.get("kind"),
            "outcome": r.get("outcome"),
            "record_id": r.get("record_id"),
        }
    return meta


def load_run(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("results") or []


def committee_pred(row: dict) -> str:
    adj = row.get("adjudication") or {}
    return norm(adj.get("final_verdict") or row.get("committee_verdict"))


def model_votes(row: dict) -> list[dict]:
    out = []
    for mr in row.get("committee", {}).get("model_results") or []:
        v = mr.get("verdict") or {}
        out.append(
            {
                "model": mr.get("model_name"),
                "verdict": norm(v.get("verdict")),
                "confidence": v.get("confidence"),
                "reasoning": (v.get("reasoning") or "")[:600],
                "evidence": v.get("evidence") or [],
            }
        )
    return out


def read_diffs(pair_dir: Path) -> tuple[str, str]:
    a = (pair_dir / "branch_a.diff").read_text(encoding="utf-8", errors="replace") if (pair_dir / "branch_a.diff").exists() else ""
    b = (pair_dir / "branch_b.diff").read_text(encoding="utf-8", errors="replace") if (pair_dir / "branch_b.diff").exists() else ""
    return a, b


def classify_error(
    *,
    corpus: str,
    family: str | None,
    gt: str,
    pred: str,
    votes: list[dict],
    a_diff: str,
    b_diff: str,
    adj: dict,
) -> dict:
    """Return category, why_wrong, root_cause based on family + rationales + diffs."""
    blob = " ".join(
        [(v.get("reasoning") or "") + " " + " ".join(map(str, v.get("evidence") or [])) for v in votes]
    ).lower()
    conflict_votes = sum(1 for v in votes if v["verdict"] == "conflict")
    compatible_votes = sum(1 for v in votes if v["verdict"] == "no_conflict")
    rule = adj.get("decision_rule") or ""

    # False positive: predicted conflict on compatible
    if gt == "no_conflict" and pred in ("conflict", "escalate"):
        # dual-API / docstring-only left branch
        if family and ("dual_api" in family or "safe_copy" in family or "orthogonal" in family):
            if any(k in blob for k in ("duplicate", "incompatible", "different function", "broken", "will break")):
                cat = "conflict_bias"
                why = "Treated additive dual-API / docstring twin as incompatible APIs"
            elif any(k in blob for k in ("rename", "stale", "import")):
                cat = "hallucination"
                why = "Hallucinated rename/stale dependency that is not in the diffs"
            elif "docstring" in a_diff.lower() or '"""' in a_diff:
                cat = "conflict_bias"
                why = "Over-weighted shared-function touch; left change is behavior-preserving"
            else:
                cat = "conflict_bias"
                why = "Predicted conflict without demonstrating a behavior break"
            # refine by family
            if family and "aliasing" in family:
                cat2 = "aliasing"
            elif family and "orthogonal" in family:
                cat2 = "conflict_bias"
            elif family and "dual_api" in family:
                cat2 = "conflict_bias"
            else:
                cat2 = cat
            root = (
                f"{conflict_votes}/{len(votes)} models voted conflict; "
                f"adjudicator rule={rule or 'committee_verdict'}; "
                "no API break / invariant violation / stale caller demonstrated"
            )
            # FPs: keep conflict_bias/hallucination/insufficient_grounding as primary;
            # family name is already in the row for stratified analysis.
            return {
                "category": cat,
                "secondary": cat2 if cat2 != cat else None,
                "error_type": "false_positive",
                "why_wrong": why,
                "root_cause": root,
            }

        # twins (hard_compatible) — family from pair name
        if corpus == "hard_compatible" or (family and family.endswith("_compat")):
            if any(k in blob for k in ("docstring", "documentation")) and conflict_votes:
                # models saw docstring but still said conflict? rare
                pass
            if any(k in blob for k in ("rename", "stale", "signature", "break")):
                cat = "hallucination"
                why = "Hallucinated semantic break on docstring-only left branch"
            else:
                cat = "conflict_bias"
                why = "Conflict-biased vote on behavior-preserving twin"
            return {
                "category": cat,
                "secondary": "insufficient_grounding",
                "error_type": "false_positive",
                "why_wrong": why,
                "root_cause": (
                    f"{conflict_votes}/{len(votes)} conflict votes; "
                    "left branch is docstring-only; original semantics preserved"
                ),
            }

        # generic FP
        if any(k in blob for k in ("might", "could", "likely", "seems", "unclear", "possible")):
            cat = "insufficient_grounding"
            why = "Speculative conflict claim without causal chain"
        elif any(k in blob for k in ("hallucin",)) or (
            "rename" in blob and "rename" not in (a_diff + b_diff).lower()
        ):
            cat = "hallucination"
            why = "Unsupported claim not present in diffs"
        else:
            cat = "conflict_bias"
            why = "Predicted conflict without evidence of broken merge behavior"
        return {
            "category": cat,
            "secondary": None,
            "error_type": "false_positive",
            "why_wrong": why,
            "root_cause": f"votes conflict={conflict_votes} compatible={compatible_votes} rule={rule}",
        }

    # False negative: predicted no_conflict / escalate on real conflict
    if gt == "conflict" and pred in ("no_conflict", "escalate"):
        fam = family or ""
        family_map = {
            "aliasing_contract": "aliasing",
            "boundary_contract": "ownership",  # boundary/threshold contract
            "ordering_default": "mutation",
            "sentinel_default": "mutation",
            "error_contract": "exception_contract",
            "case_sensitivity": "ownership",
        }
        # better mapping per user taxonomy
        family_map = {
            "aliasing_contract": "aliasing",
            "boundary_contract": "ownership",
            "ordering_default": "mutation",
            "sentinel_default": "mutation",
            "error_contract": "exception_contract",
            "case_sensitivity": "stale_rename",  # not rename but contract; use ownership
        }
        # refine
        if "aliasing" in fam:
            cat = "aliasing"
            why = "Ignored copy-vs-alias / ownership mutation hazard"
        elif "error" in fam:
            cat = "exception_contract"
            why = "Missed exception-contract change (silent fallback vs raise)"
        elif "boundary" in fam:
            cat = "ownership"
            why = "Missed boundary/threshold contract change"
        elif "ordering" in fam or "sentinel" in fam:
            cat = "mutation"
            why = "Missed default-semantics / sentinel mutation"
        elif "case" in fam:
            cat = "ownership"
            why = "Missed case-sensitivity contract"
        elif "rename" in fam or "stale" in fam:
            cat = "stale_rename"
            why = "Missed rename → stale caller"
        else:
            cat = "insufficient_grounding"
            why = "Failed to ground conflict evidence from diffs"

        if pred == "escalate":
            why = f"Escalated instead of deciding; {why}"
            secondary = "insufficient_grounding"
        elif compatible_votes >= conflict_votes:
            secondary = "insufficient_grounding"
        else:
            secondary = None

        return {
            "category": cat,
            "secondary": secondary,
            "error_type": "false_negative" if pred == "no_conflict" else "escalation_miss",
            "why_wrong": why,
            "root_cause": (
                f"votes conflict={conflict_votes} compatible={compatible_votes} "
                f"rule={rule}; family={fam}"
            ),
        }

    # escalate counted as wrong already above; residual
    return {
        "category": "insufficient_grounding",
        "secondary": None,
        "error_type": "other",
        "why_wrong": f"Unexpected pred={pred} gt={gt}",
        "root_cause": rule,
    }


def analyze_corpus(
    name: str,
    rows: list[dict],
    pairs_root: Path,
    sealed: dict[str, dict],
) -> list[dict]:
    errors = []
    for row in rows:
        gt = norm(row.get("ground_truth"))
        pred = committee_pred(row)
        if pred == gt:
            continue
        pair = row["pair"]
        sm = sealed.get(pair) or {}
        family = sm.get("family")
        label_path = pairs_root / pair / "label.json"
        if family is None and label_path.exists():
            lab = json.loads(label_path.read_text(encoding="utf-8"))
            family = lab.get("conflict_type") or lab.get("family")
        # twin pair names encode family
        if family is None and pair.startswith("twin_"):
            # twin_boundary_contract_0001
            parts = pair.split("_")
            if len(parts) >= 3:
                family = "_".join(parts[1:-1]) + "_compat"

        votes = model_votes(row)
        a_diff, b_diff = read_diffs(pairs_root / pair)
        adj = row.get("adjudication") or {}
        clf = classify_error(
            corpus=name,
            family=family,
            gt=gt,
            pred=pred,
            votes=votes,
            a_diff=a_diff,
            b_diff=b_diff,
            adj=adj,
        )
        errors.append(
            {
                "corpus": name,
                "pair": pair,
                "family": family,
                "ground_truth": gt,
                "committee": pred,
                "baseline": norm(row.get("baseline_verdict")),
                "majority": _majority(votes),
                "error_type": clf["error_type"],
                "category": clf["category"],
                "secondary": clf.get("secondary"),
                "why_wrong": clf["why_wrong"],
                "root_cause": clf["root_cause"],
                "decision_rule": adj.get("decision_rule"),
                "model_votes": votes,
                "adjudication_explanation": (adj.get("explanation") or "")[:400],
            }
        )
    return errors


def _majority(votes: list[dict]) -> str:
    c = Counter(v["verdict"] for v in votes if v["verdict"] in ("conflict", "no_conflict"))
    if not c:
        return "escalate"
    top = c.most_common()
    if len(top) > 1 and top[0][1] == top[1][1]:
        return "escalate"
    return top[0][0]


def main() -> None:
    sealed = sealed_meta()
    corpora = []

    blind = load_run(RESULTS / "run_blind_eval_raw_final.json")
    if blind:
        corpora.append(("blind_eval", blind, PAIRS_BLIND))

    hard = load_run(RESULTS / "run_20260718T224427Z.json")
    if hard:
        corpora.append(("hard_negatives", hard, PAIRS_NEG))

    twins = load_run(RESULTS / "twins_raw_checkpoint.json")
    if not twins:
        twins = load_run(RESULTS / "run_hard_compatible_raw_final.json")
    if twins:
        corpora.append(("hard_compatible", twins, PAIRS_TWIN))

    all_errors: list[dict] = []
    corpus_stats = {}
    for name, rows, root in corpora:
        errs = analyze_corpus(name, rows, root, sealed)
        all_errors.extend(errs)
        n = len(rows)
        correct = n - len(errs)
        fp = sum(1 for e in errs if e["error_type"] == "false_positive")
        fn = sum(1 for e in errs if e["error_type"] == "false_negative")
        esc = sum(1 for e in errs if e["error_type"] == "escalation_miss")
        corpus_stats[name] = {
            "n": n,
            "errors": len(errs),
            "correct": correct,
            "accuracy": correct / n if n else 0,
            "false_positives": fp,
            "false_negatives": fn,
            "escalation_misses": esc,
            "by_category": dict(Counter(e["category"] for e in errs)),
            "labels": dict(Counter(norm(r["ground_truth"]) for r in rows)),
        }

    catalog = {
        "generated_for": "Priority 1 — every committee mistake",
        "policy": "diagnostic only; no adjudicator changes",
        "corpus_stats": corpus_stats,
        "category_totals": dict(Counter(e["category"] for e in all_errors)),
        "error_type_totals": dict(Counter(e["error_type"] for e in all_errors)),
        "errors": all_errors,
    }
    (RESULTS / "error_catalog.json").write_text(
        json.dumps(catalog, indent=2) + "\n", encoding="utf-8"
    )

    # Markdown report
    md = [
        "# Committee Mistake Catalog (Priority 1)",
        "",
        "Diagnostic only — no model/adjudicator changes.",
        "",
        "## Headline",
        "",
    ]
    for name, st in corpus_stats.items():
        md.append(
            f"- **{name}**: {st['errors']}/{st['n']} errors "
            f"(acc={st['accuracy']:.1%}) · FP={st['false_positives']} "
            f"FN={st['false_negatives']} esc-miss={st['escalation_misses']} · "
            f"labels={st['labels']}"
        )
    md.append("")
    md.append("## Category totals (all corpora)")
    md.append("")
    md.append("| Category | Count |")
    md.append("|---|---:|")
    for cat, n in sorted(catalog["category_totals"].items(), key=lambda x: -x[1]):
        md.append(f"| `{cat}` | {n} |")
    md.append("")

    md.append("## Dominant finding: conflict bias")
    md.append("")
    md.append(
        "On the leakage-free blind benchmark, the evidence-weighted committee scored "
        "**TN=0 / FP=100** on all compatible pairs (every dual-API twin and orthogonal "
        "pair predicted conflict). Majority vote is identical (always conflict). "
        "Baseline is the opposite extreme (always no_conflict). "
        "The committee's single largest weakness is accepting vague 'semantic "
        "incompatibility' without requiring evidence of an actual behavior break."
    )
    md.append("")

    # Per-corpus tables
    for name, _, _ in corpora:
        errs = [e for e in all_errors if e["corpus"] == name]
        md.append(f"## {name} — every error ({len(errs)})")
        md.append("")
        md.append("| Pair | Family | GT | Committee | Why wrong | Category | Root cause |")
        md.append("|---|---|---|---|---|---|---|")
        for e in errs:
            why = e["why_wrong"].replace("|", "/")
            root = e["root_cause"].replace("|", "/")[:120]
            md.append(
                f"| `{e['pair']}` | {e['family'] or '-'} | {e['ground_truth']} | "
                f"{e['committee']} | {why} | `{e['category']}` | {root} |"
            )
        md.append("")

        # Family × category crosstab for blind
        if name == "blind_eval":
            md.append("### Blind family × error category")
            md.append("")
            fams = sorted({e["family"] for e in errs if e["family"]})
            cats = sorted({e["category"] for e in errs})
            md.append("| Family | " + " | ".join(f"`{c}`" for c in cats) + " | Total |")
            md.append("|---|" + "|".join(["---:"] * len(cats)) + "|---:|")
            for fam in fams:
                row = [e for e in errs if e["family"] == fam]
                cells = [str(sum(1 for e in row if e["category"] == c)) for c in cats]
                md.append(f"| {fam} | " + " | ".join(cells) + f" | {len(row)} |")
            md.append("")

    # Sample deep dives
    md.append("## Deep dives (representative mistakes)")
    md.append("")
    samples = []
    # one FP dual-api, one FP orthogonal, one FN aliasing if present
    for e in all_errors:
        if e["corpus"] == "blind_eval" and e["error_type"] == "false_positive" and e["family"] and "dual_api" in e["family"]:
            samples.append(e)
            break
    for e in all_errors:
        if e["corpus"] == "blind_eval" and e["family"] == "cross_file_orthogonal":
            samples.append(e)
            break
    for e in all_errors:
        if e["error_type"] == "false_negative" and e["category"] == "aliasing":
            samples.append(e)
            break
    for e in all_errors:
        if e["corpus"] == "hard_compatible" and e["error_type"] == "false_positive":
            samples.append(e)
            break

    for e in samples:
        md.append(f"### `{e['pair']}` ({e['corpus']})")
        md.append("")
        md.append(f"- GT: **{e['ground_truth']}** · Committee: **{e['committee']}** · Baseline: {e['baseline']}")
        md.append(f"- Family: `{e['family']}`")
        md.append(f"- Category: `{e['category']}` — {e['why_wrong']}")
        md.append(f"- Root cause: {e['root_cause']}")
        md.append(f"- Adjudication: `{e['decision_rule']}` — {(e.get('adjudication_explanation') or '')[:240]}")
        md.append("- Model votes:")
        for v in e["model_votes"]:
            md.append(
                f"  - `{v['model']}` → `{v['verdict']}` (conf={v['confidence']}): "
                f"{(v['reasoning'] or '')[:200]}"
            )
        md.append("")

    md.append("## Implications for Priority 2–3 (do not implement yet)")
    md.append("")
    md.append(
        "1. **Conflict bias** dominates: every blind compatible pair was labeled conflict. "
        "Adjudication must require evidence of an *actual behavior break* "
        "(API break, violated invariant, stale caller, ownership violation, contract mismatch), "
        "not mere 'semantic difference' or 'duplicate helpers'."
    )
    md.append(
        "2. **Evidence scoring** currently rewards identifier overlap and confident "
        "conflict narratives; it does not penalize speculative / hallucinated breaks on "
        "docstring-only or dual-API twins."
    )
    md.append(
        "3. False negatives on hard conflicts are fewer and concentrated in "
        "aliasing / ordering / sentinel / error families where the invariant is subtle."
    )
    md.append("")
    md.append("## Artifacts")
    md.append("")
    md.append("- `results/error_catalog.json` — full machine-readable catalog")
    md.append("- `results/error_analysis.md` — this report")
    md.append("")

    (RESULTS / "error_analysis.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # Compact CSV-like table for quick scan
    lines = ["pair,corpus,family,gt,committee,error_type,category,why_wrong"]
    for e in all_errors:
        why = e["why_wrong"].replace(",", ";")
        lines.append(
            f"{e['pair']},{e['corpus']},{e['family'] or ''},{e['ground_truth']},"
            f"{e['committee']},{e['error_type']},{e['category']},{why}"
        )
    (RESULTS / "error_catalog.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Catalogued {len(all_errors)} mistakes across {len(corpora)} corpora")
    print(json.dumps(corpus_stats, indent=2))
    print("categories", catalog["category_totals"])


if __name__ == "__main__":
    main()
