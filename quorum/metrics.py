"""Evaluation metrics for conflict detection with abstention."""

from __future__ import annotations

import json
from collections import Counter
from itertools import combinations
from typing import Any

from quorum.models import normalize_verdict

CANONICAL_LABELS = ("conflict", "no_conflict")


def _canonical(value: Any) -> str:
    if value in {"escalate", "error"}:
        return str(value)
    return normalize_verdict(value) or "error"


def majority_prediction(row: dict[str, Any]) -> str:
    votes: Counter[str] = Counter()
    for result in row["committee"]["model_results"]:
        verdict = result.get("verdict")
        if result.get("outcome") == "ok" and verdict:
            votes[_canonical(verdict.get("verdict"))] += 1
    ranked = votes.most_common()
    if not ranked or (len(ranked) > 1 and ranked[0][1] == ranked[1][1]):
        return "escalate"
    return ranked[0][0]


def _model_prediction(row: dict[str, Any], model_name: str) -> str:
    for result in row["committee"]["model_results"]:
        if result["model_name"] != model_name:
            continue
        verdict = result.get("verdict")
        if result.get("outcome") == "ok" and verdict:
            return _canonical(verdict.get("verdict"))
        return "error"
    return "error"


def _predictions(
    results: list[dict[str, Any]],
    system: str,
) -> list[tuple[str, str]]:
    predictions: list[tuple[str, str]] = []
    for row in results:
        truth = _canonical(row.get("ground_truth"))
        if system == "baseline":
            prediction = _canonical(row.get("baseline_verdict"))
        elif system == "committee":
            prediction = _canonical(row.get("committee_verdict"))
        elif system == "majority_vote":
            prediction = majority_prediction(row)
        else:
            prediction = _model_prediction(row, system)
        predictions.append((truth, prediction))
    return predictions


def _average_latency(results: list[dict[str, Any]], system: str) -> float:
    latencies: list[float] = []
    for row in results:
        if system == "baseline":
            latencies.append(float(row["baseline"]["wall_clock_seconds"]))
        elif system in {"committee", "majority_vote"}:
            latencies.append(float(row["committee"]["wall_clock_seconds"]))
        else:
            for result in row["committee"]["model_results"]:
                if result["model_name"] == system:
                    latencies.append(float(result.get("elapsed_seconds", 0.0)))
                    break
    return sum(latencies) / len(latencies) if latencies else 0.0


def system_metrics(
    results: list[dict[str, Any]],
    system: str,
) -> dict[str, Any]:
    pairs = _predictions(results, system)
    total = len(pairs)
    tp = fp = tn = fn = escalated = errors = correct = 0
    for truth, prediction in pairs:
        if prediction == "escalate":
            escalated += 1
            continue
        if prediction == "error":
            errors += 1
            continue
        if prediction == truth:
            correct += 1
        if truth == "conflict" and prediction == "conflict":
            tp += 1
        elif truth == "no_conflict" and prediction == "conflict":
            fp += 1
        elif truth == "no_conflict" and prediction == "no_conflict":
            tn += 1
        elif truth == "conflict" and prediction == "no_conflict":
            fn += 1

    decided = tp + fp + tn + fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    return {
        "total": total,
        "correct": correct,
        "accuracy": correct / total if total else 0.0,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "escalations": escalated,
        "escalation_rate": escalated / total if total else 0.0,
        "errors": errors,
        "coverage": decided / total if total else 0.0,
        "decided_accuracy": correct / decided if decided else 0.0,
        "confusion_matrix": {
            "true_conflict_pred_conflict": tp,
            "true_no_conflict_pred_conflict": fp,
            "true_no_conflict_pred_no_conflict": tn,
            "true_conflict_pred_no_conflict": fn,
            "escalate": escalated,
            "error": errors,
        },
        "average_latency_seconds": _average_latency(results, system),
    }


def pairwise_agreement(
    results: list[dict[str, Any]],
    model_names: list[str],
) -> dict[str, Any]:
    agreement: dict[str, Any] = {}
    for left, right in combinations(model_names, 2):
        comparable = matches = 0
        for row in results:
            left_vote = _model_prediction(row, left)
            right_vote = _model_prediction(row, right)
            if left_vote in CANONICAL_LABELS and right_vote in CANONICAL_LABELS:
                comparable += 1
                matches += int(left_vote == right_vote)
        agreement[f"{left}__{right}"] = {
            "matches": matches,
            "comparable": comparable,
            "rate": matches / comparable if comparable else 0.0,
        }
    return agreement


def score_evaluation(results: list[dict[str, Any]]) -> dict[str, Any]:
    model_names = sorted(
        {
            result["model_name"]
            for row in results
            for result in row["committee"]["model_results"]
        }
    )
    systems = {
        "baseline": system_metrics(results, "baseline"),
        "individual_models": {
            model: system_metrics(results, model) for model in model_names
        },
        "majority_vote": system_metrics(results, "majority_vote"),
        "committee": system_metrics(results, "committee"),
    }
    systems["per_model_agreement"] = pairwise_agreement(results, model_names)
    systems["runtime_seconds"] = sum(
        float(row["baseline"]["wall_clock_seconds"])
        + float(row["committee"]["wall_clock_seconds"])
        for row in results
    )
    return systems


def _percentage(value: float) -> str:
    return f"{100 * value:.1f}%"


def comparison_markdown(
    raw: dict[str, Any],
    structured: dict[str, Any],
    timestamp: str,
    pair_count: int,
) -> str:
    lines = [
        "# CooperBench Python: Raw Diff vs Structured AST",
        "",
        f"- Timestamp: `{timestamp}`",
        f"- Pairs: {pair_count}",
        "- Positive class: `conflict`",
        "- Precision/recall/F1 use non-escalated predictions; coverage reports "
        "the evaluated fraction.",
        "",
        "| Representation | System | Accuracy | Precision | Recall | F1 | "
        "Escalations | Coverage | Avg latency | Runtime |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for representation, score in (("Raw Diff", raw), ("Structured AST", structured)):
        for system in ("baseline", "majority_vote", "committee"):
            metric = score[system]
            lines.append(
                f"| {representation} | {system} | "
                f"{_percentage(metric['accuracy'])} | "
                f"{_percentage(metric['precision'])} | "
                f"{_percentage(metric['recall'])} | "
                f"{_percentage(metric['f1'])} | "
                f"{metric['escalations']} ({_percentage(metric['escalation_rate'])}) | "
                f"{_percentage(metric['coverage'])} | "
                f"{metric['average_latency_seconds']:.1f}s | "
                f"{score['runtime_seconds']:.1f}s |"
            )
    lines.extend(
        [
            "",
            "## Individual models",
            "",
            "| Model | Raw accuracy | Structured accuracy | Raw F1 | Structured F1 | "
            "Raw latency | Structured latency |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    all_models = sorted(
        set(raw["individual_models"]) | set(structured["individual_models"])
    )
    for model in all_models:
        raw_model = raw["individual_models"][model]
        structured_model = structured["individual_models"][model]
        lines.append(
            f"| {model} | {_percentage(raw_model['accuracy'])} | "
            f"{_percentage(structured_model['accuracy'])} | "
            f"{_percentage(raw_model['f1'])} | "
            f"{_percentage(structured_model['f1'])} | "
            f"{raw_model['average_latency_seconds']:.1f}s | "
            f"{structured_model['average_latency_seconds']:.1f}s |"
        )
    lines.extend(
        [
            "",
            "## Per-model agreement",
            "",
            "```json",
            json.dumps(
                {
                    "raw": raw["per_model_agreement"],
                    "structured": structured["per_model_agreement"],
                },
                indent=2,
            ),
            "```",
            "",
            "## Confusion matrices",
            "",
            "```json",
            json.dumps(
                {
                    "raw": {
                        "baseline": raw["baseline"]["confusion_matrix"],
                        "majority_vote": raw["majority_vote"]["confusion_matrix"],
                        "committee": raw["committee"]["confusion_matrix"],
                    },
                    "structured": {
                        "baseline": structured["baseline"]["confusion_matrix"],
                        "majority_vote": structured["majority_vote"][
                            "confusion_matrix"
                        ],
                        "committee": structured["committee"]["confusion_matrix"],
                    },
                },
                indent=2,
            ),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def concise_comparison_report(
    raw: dict[str, Any],
    structured: dict[str, Any],
) -> str:
    raw_committee = raw["committee"]
    structured_committee = structured["committee"]

    def summary_line(metric: dict[str, Any]) -> str:
        return (
            f"accuracy={_percentage(metric['accuracy'])}, "
            f"P={_percentage(metric['precision'])}, "
            f"R={_percentage(metric['recall'])}, "
            f"F1={_percentage(metric['f1'])}, "
            f"escalations={metric['escalations']}, "
            f"coverage={_percentage(metric['coverage'])}"
        )

    def delta(key: str) -> str:
        change = structured_committee[key] - raw_committee[key]
        return f"{100 * change:+.1f} pp"

    raw_baseline = raw["baseline"]
    structured_baseline = structured["baseline"]
    representation_gain = (
        structured_baseline["f1"] > raw_baseline["f1"]
        or structured_baseline["recall"] > raw_baseline["recall"]
    )
    committee_over_escalates = (
        structured_committee["escalation_rate"] >= 0.75
        and raw_committee["escalation_rate"] >= 0.75
    )
    if representation_gain and committee_over_escalates:
        recommendation = (
            "Use structured AST by default for Python baseline/majority-vote "
            "scoring; keep evidence-adjudicated committee as an escalation layer "
            "because it currently abstains on most CooperBench pairs in both modes."
        )
    elif representation_gain:
        recommendation = "Use structured AST by default for Python."
    else:
        recommendation = (
            "Keep raw diffs as the default; structured AST showed no measured gain."
        )
    model_lines = []
    for model in sorted(structured["individual_models"]):
        raw_model = raw["individual_models"][model]
        structured_model = structured["individual_models"][model]
        model_lines.append(
            f"  {model}: raw={_percentage(raw_model['accuracy'])}, "
            f"structured={_percentage(structured_model['accuracy'])}"
        )
    def baseline_delta(key: str) -> str:
        change = structured_baseline[key] - raw_baseline[key]
        return f"{100 * change:+.1f} pp"

    return "\n".join(
        [
            "============================",
            "COOPERBENCH COMPARISON",
            "============================",
            "",
            "Raw",
            f"  Baseline: {summary_line(raw_baseline)}",
            f"  Majority: {summary_line(raw['majority_vote'])}",
            f"  Committee: {summary_line(raw_committee)}",
            "",
            "Structured",
            f"  Baseline: {summary_line(structured_baseline)}",
            f"  Majority: {summary_line(structured['majority_vote'])}",
            f"  Committee: {summary_line(structured_committee)}",
            "",
            "Improvement (baseline):",
            f"  Accuracy: {baseline_delta('accuracy')}",
            f"  Precision: {baseline_delta('precision')}",
            f"  Recall: {baseline_delta('recall')}",
            f"  F1: {baseline_delta('f1')}",
            f"  Escalations: "
            f"{structured_committee['escalations'] - raw_committee['escalations']:+d}",
            f"  Coverage: {baseline_delta('coverage')}",
            "",
            "Per-model:",
            *model_lines,
            "",
            "Recommendation:",
            f"  {recommendation}",
            "============================",
        ]
    )
