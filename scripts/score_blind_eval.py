"""Score a blind_eval run against sealed labels. Fair, leakage-free metrics.

Usage:
    python scripts/score_blind_eval.py [results/blind_raw_checkpoint.json]

Reports per system (Baseline / Majority vote / Evidence-weighted committee):
    confusion matrix (conflict = positive), precision, recall/sensitivity,
    specificity, F1, balanced accuracy, MCC, coverage, escalation rate.
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SEALED = ROOT / "dataset" / "blind_eval" / "labels.sealed.jsonl"
DEFAULT_RUN = RESULTS / "blind_raw_checkpoint.json"


def norm(v: str | None) -> str | None:
    if v is None:
        return None
    v = str(v).strip().lower()
    if v == "conflict":
        return "conflict"
    if v in {"no_conflict", "compatible", "clean_merge", "safe"}:
        return "no_conflict"
    if v in {"escalate", "abstain"}:
        return "escalate"
    return v


def sealed_family() -> dict[str, str]:
    fam = {}
    for line in SEALED.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            fam[str(r["pair_id"])] = r.get("family", "?")
    return fam


def majority_vote(row: dict) -> str:
    votes = []
    for mr in row["committee"]["model_results"]:
        if mr.get("outcome") != "ok" or not mr.get("verdict"):
            continue
        votes.append(norm(mr["verdict"].get("verdict")))
    c = Counter(v for v in votes if v in {"conflict", "no_conflict"})
    if not c:
        return "escalate"
    top = c.most_common()
    if len(top) > 1 and top[0][1] == top[1][1]:
        return "escalate"
    return top[0][0]


def evidence_weighted(row: dict) -> str:
    return norm((row.get("adjudication") or {}).get("final_verdict"))


def confusion(y_true, y_pred, positive="conflict"):
    tp = fp = tn = fn = 0
    decided = 0
    escalated = 0
    for t, p in zip(y_true, y_pred):
        if p not in {"conflict", "no_conflict"}:
            escalated += 1
            # escalate scored as incorrect (not a decision)
            if t == positive:
                fn += 1
            else:
                fp += 1
            continue
        decided += 1
        if t == positive and p == positive:
            tp += 1
        elif t != positive and p == positive:
            fp += 1
        elif t != positive and p != positive:
            tn += 1
        else:
            fn += 1
    n = len(y_true)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    sens = tp / (tp + fn) if (tp + fn) else 0.0
    spec = tn / (tn + fp) if (tn + fp) else 0.0
    f1 = 2 * prec * sens / (prec + sens) if (prec + sens) else 0.0
    bal = 0.5 * (sens + spec)
    denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = ((tp * tn) - (fp * fn)) / denom if denom else 0.0
    return {
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "precision": prec,
        "recall_sensitivity": sens,
        "specificity": spec,
        "f1": f1,
        "balanced_accuracy": bal,
        "mcc": mcc,
        "accuracy": (tp + tn) / n if n else 0.0,
        "coverage": decided / n if n else 0.0,
        "escalation_rate": escalated / n if n else 0.0,
    }


def main() -> None:
    run_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_RUN
    data = json.loads(run_path.read_text(encoding="utf-8"))
    rows = data["results"]
    fam = sealed_family()

    y_true = [norm(r["ground_truth"]) for r in rows]
    systems = {
        "Baseline (single LLM)": [norm(r["baseline_verdict"]) for r in rows],
        "Majority vote": [majority_vote(r) for r in rows],
        "Evidence-weighted committee": [evidence_weighted(r) for r in rows],
    }
    metrics = {name: confusion(y_true, preds) for name, preds in systems.items()}

    # Per-family committee accuracy
    per_family = {}
    for r in rows:
        f = fam.get(r["pair"], "?")
        d = per_family.setdefault(f, {"n": 0, "committee_correct": 0})
        d["n"] += 1
        if evidence_weighted(r) == norm(r["ground_truth"]):
            d["committee_correct"] += 1

    payload = {
        "run": run_path.name,
        "n_scored": len(rows),
        "label_balance": dict(Counter(y_true)),
        "systems": metrics,
        "per_family_committee": per_family,
        "leakage_free": True,
        "notes": "context.md omitted from all prompts; labels read only for scoring.",
    }
    (RESULTS / "blind_eval_metrics.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )

    md = [
        "# Blind Evaluation Report",
        "",
        f"- Run: `{run_path.name}` (raw, leakage-free)",
        f"- Scored: **{len(rows)}** pairs · balance {dict(Counter(y_true))}",
        "- Prompts contain no `context.md`, no ground-truth, no filenames with labels.",
        "",
        "## Systems (conflict = positive)",
        "",
        "| System | Acc | Prec | Recall | Spec | F1 | BalAcc | MCC | Cov | Esc |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, m in metrics.items():
        md.append(
            f"| {name} | {m['accuracy']:.1%} | {m['precision']:.1%} | "
            f"{m['recall_sensitivity']:.1%} | {m['specificity']:.1%} | {m['f1']:.1%} | "
            f"{m['balanced_accuracy']:.1%} | {m['mcc']:.2f} | {m['coverage']:.1%} | "
            f"{m['escalation_rate']:.1%} |"
        )
    md.append("")
    md.append("## Confusion matrices")
    md.append("")
    for name, m in metrics.items():
        md.append(f"### {name}")
        md.append("")
        md.append("|  | Pred conflict | Pred no_conflict/esc |")
        md.append("|---|---:|---:|")
        md.append(f"| **Truth conflict** | TP={m['TP']} | FN={m['FN']} |")
        md.append(f"| **Truth no_conflict** | FP={m['FP']} | TN={m['TN']} |")
        md.append("")
    md.append("## Per-family committee accuracy")
    md.append("")
    md.append("| Family | N | Committee correct |")
    md.append("|---|---:|---:|")
    for f, d in sorted(per_family.items()):
        md.append(f"| {f} | {d['n']} | {d['committee_correct']}/{d['n']} |")
    md.append("")
    (RESULTS / "blind_eval_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"Scored {len(rows)} pairs from {run_path.name}")
    for name, m in metrics.items():
        print(
            f"  {name}: acc={m['accuracy']:.1%} F1={m['f1']:.1%} "
            f"BalAcc={m['balanced_accuracy']:.1%} MCC={m['mcc']:.2f} "
            f"(TP={m['TP']} FP={m['FP']} TN={m['TN']} FN={m['FN']})"
        )


if __name__ == "__main__":
    main()
