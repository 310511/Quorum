"""Offline comparison of saved committee decisions vs behavior-break adjudication."""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quorum.ablation import _reconstruct_model_results
from quorum.adjudicate_v2 import adjudicate_v2
from quorum.models import normalize_verdict

RESULTS = ROOT / "results"

CORPORA = (
    (
        "blind_eval",
        RESULTS / "run_blind_eval_raw_final.json",
        ROOT / "data" / "pairs" / "blind_eval",
    ),
    (
        "hard_negatives",
        RESULTS / "run_20260718T224427Z.json",
        ROOT / "data" / "pairs" / "hard_negatives",
    ),
    (
        "hard_compatible_partial",
        RESULTS / "twins_raw_checkpoint.json",
        ROOT / "data" / "pairs" / "hard_compatible",
    ),
)


def _prediction(row: dict) -> str:
    adjudication = row.get("adjudication") or {}
    return normalize_verdict(
        adjudication.get("final_verdict") or row.get("committee_verdict")
    ) or "error"


def _metrics(truths: list[str], predictions: list[str]) -> dict:
    tp = fp = tn = fn = escalations = 0
    for truth, prediction in zip(truths, predictions):
        if prediction == "escalate":
            escalations += 1
            if truth == "conflict":
                fn += 1
            else:
                fp += 1
        elif truth == "conflict" and prediction == "conflict":
            tp += 1
        elif truth == "no_conflict" and prediction == "conflict":
            fp += 1
        elif truth == "no_conflict" and prediction == "no_conflict":
            tn += 1
        else:
            fn += 1
    n = len(truths)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    denominator = math.sqrt(
        (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    )
    mcc = ((tp * tn) - (fp * fn)) / denominator if denominator else 0.0
    return {
        "accuracy": (tp + tn) / n if n else 0.0,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "f1": f1,
        "balanced_accuracy": (recall + specificity) / 2,
        "mcc": mcc,
        "escalation_rate": escalations / n if n else 0.0,
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "escalations": escalations,
    }


def evaluate(name: str, run_path: Path, pairs_root: Path) -> dict | None:
    if not run_path.exists():
        return None
    rows = json.loads(run_path.read_text(encoding="utf-8")).get("results") or []
    truths: list[str] = []
    old_predictions: list[str] = []
    new_predictions: list[str] = []
    rules: Counter[str] = Counter()
    changed: list[dict] = []

    for row in rows:
        pair_dir = pairs_root / row["pair"]
        branch_a = (pair_dir / "branch_a.diff").read_text(encoding="utf-8")
        branch_b = (pair_dir / "branch_b.diff").read_text(encoding="utf-8")
        outcome = adjudicate_v2(
            _reconstruct_model_results(row),
            branch_a_diff=branch_a,
            branch_b_diff=branch_b,
        )
        truth = normalize_verdict(row.get("ground_truth")) or "error"
        old = _prediction(row)
        new = outcome.final_verdict
        truths.append(truth)
        old_predictions.append(old)
        new_predictions.append(new)
        rules[outcome.decision_rule] += 1
        if old != new:
            changed.append(
                {
                    "pair": row["pair"],
                    "truth": truth,
                    "old": old,
                    "new": new,
                    "rule": outcome.decision_rule,
                    "explanation": outcome.explanation,
                }
            )

    return {
        "corpus": name,
        "run": run_path.name,
        "n": len(rows),
        "old": _metrics(truths, old_predictions),
        "new": _metrics(truths, new_predictions),
        "new_rule_counts": dict(rules),
        "changed_predictions": changed,
    }


def main() -> None:
    corpora = [
        result
        for name, run_path, pairs_root in CORPORA
        if (result := evaluate(name, run_path, pairs_root)) is not None
    ]
    output = {"policy": "behavior_break_gate_v3", "corpora": corpora}
    (RESULTS / "adjudicator_v3_offline.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )

    report = [
        "# Behavior-Break Adjudicator — Offline Evaluation",
        "",
        "Same saved model outputs; only adjudication/scoring changed.",
        "",
        "| Corpus | N | Policy | Acc | Prec | Recall | Spec | F1 | BalAcc | MCC | Esc |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for corpus in corpora:
        for label in ("old", "new"):
            metrics = corpus[label]
            report.append(
                f"| {corpus['corpus']} | {corpus['n']} | {label} | "
                f"{metrics['accuracy']:.1%} | {metrics['precision']:.1%} | "
                f"{metrics['recall']:.1%} | {metrics['specificity']:.1%} | "
                f"{metrics['f1']:.1%} | {metrics['balanced_accuracy']:.1%} | "
                f"{metrics['mcc']:.2f} | {metrics['escalation_rate']:.1%} |"
            )
        report.extend(
            [
                "",
                f"New confusion: `{corpus['new']['TP']=}` "
                f"`{corpus['new']['FP']=}` `{corpus['new']['TN']=}` "
                f"`{corpus['new']['FN']=}`",
                "",
                f"Rules: `{corpus['new_rule_counts']}`",
                "",
            ]
        )
    (RESULTS / "adjudicator_v3_offline.md").write_text(
        "\n".join(report) + "\n", encoding="utf-8"
    )

    for corpus in corpora:
        old = corpus["old"]
        new = corpus["new"]
        print(
            f"{corpus['corpus']} N={corpus['n']}: "
            f"acc {old['accuracy']:.1%}->{new['accuracy']:.1%}, "
            f"spec {old['specificity']:.1%}->{new['specificity']:.1%}, "
            f"recall {old['recall']:.1%}->{new['recall']:.1%}, "
            f"F1 {old['f1']:.1%}->{new['f1']:.1%}, "
            f"MCC {old['mcc']:.2f}->{new['mcc']:.2f}"
        )


if __name__ == "__main__":
    main()
