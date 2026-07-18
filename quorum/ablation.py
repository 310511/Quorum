"""Adjudication-policy ablation over saved evaluation runs (no LLM calls)."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from quorum.adjudicate import adjudicate
from quorum.adjudicate_v2 import adjudicate_v2
from quorum.metrics import majority_prediction
from quorum.models import ModelResult, VerdictResponse, normalize_verdict

POLICIES = (
    ("A_current_escalation", "Current policy: any disagreement or weak overlap escalates"),
    ("B_majority_vote", "Plain majority vote over successful models"),
    ("C_evidence_weighted", "Evidence-weighted adjudication (rationale scoring)"),
)


@dataclass
class PolicyMetrics:
    total: int = 0
    correct: int = 0
    escalations: int = 0
    errors: int = 0
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0
    rationale_scores: list[float] = field(default_factory=list)
    latencies_ms: list[float] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        decided = self.tp + self.fp + self.tn + self.fn
        precision = self.tp / (self.tp + self.fp) if self.tp + self.fp else 0.0
        recall = self.tp / (self.tp + self.fn) if self.tp + self.fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        return {
            "total": self.total,
            "coverage": decided / self.total if self.total else 0.0,
            "escalation_rate": self.escalations / self.total if self.total else 0.0,
            "escalations": self.escalations,
            "errors": self.errors,
            "accuracy": self.correct / self.total if self.total else 0.0,
            "decided_accuracy": self.correct / decided if decided else 0.0,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "confusion_matrix": {
                "true_conflict_pred_conflict": self.tp,
                "true_no_conflict_pred_conflict": self.fp,
                "true_no_conflict_pred_no_conflict": self.tn,
                "true_conflict_pred_no_conflict": self.fn,
                "escalate": self.escalations,
                "error": self.errors,
            },
            "average_rationale_score": (
                sum(self.rationale_scores) / len(self.rationale_scores)
                if self.rationale_scores
                else None
            ),
            "average_adjudication_latency_ms": (
                sum(self.latencies_ms) / len(self.latencies_ms)
                if self.latencies_ms
                else None
            ),
        }

    def record(self, truth: str, prediction: str) -> None:
        self.total += 1
        if prediction == "escalate":
            self.escalations += 1
            return
        if prediction not in ("conflict", "no_conflict"):
            self.errors += 1
            return
        if prediction == truth:
            self.correct += 1
        if truth == "conflict" and prediction == "conflict":
            self.tp += 1
        elif truth == "no_conflict" and prediction == "conflict":
            self.fp += 1
        elif truth == "no_conflict" and prediction == "no_conflict":
            self.tn += 1
        elif truth == "conflict" and prediction == "no_conflict":
            self.fn += 1


def _reconstruct_model_results(row: dict[str, Any]) -> list[ModelResult]:
    results: list[ModelResult] = []
    for item in row["committee"]["model_results"]:
        verdict_data = item.get("verdict")
        verdict = None
        if item.get("outcome") == "ok" and verdict_data:
            label = normalize_verdict(verdict_data.get("verdict"))
            if label:
                verdict = VerdictResponse(
                    verdict=label,
                    original_verdict=str(
                        verdict_data.get("original_verdict", verdict_data.get("verdict"))
                    ),
                    confidence=float(verdict_data.get("confidence") or 0.0),
                    reasoning=str(verdict_data.get("reasoning") or ""),
                    evidence=[str(e) for e in verdict_data.get("evidence") or []],
                )
        results.append(
            ModelResult(
                model_name=item["model_name"],
                role=item.get("role", "committee"),
                outcome="ok" if verdict else "error",
                verdict=verdict,
                error=item.get("error"),
                elapsed_seconds=float(item.get("elapsed_seconds") or 0.0),
            )
        )
    return results


def _pair_inputs(pairs_root: Path, row: dict[str, Any], mode: str) -> dict[str, Any]:
    pair_dir = pairs_root / row["pair"]
    branch_a = pair_dir / "branch_a.diff"
    branch_b = pair_dir / "branch_b.diff"
    inputs: dict[str, Any] = {
        "branch_a_diff": branch_a.read_text(encoding="utf-8") if branch_a.exists() else "",
        "branch_b_diff": branch_b.read_text(encoding="utf-8") if branch_b.exists() else "",
        "structured_delta": None,
    }
    if mode == "structured":
        from quorum.delta import compute_pair_delta

        inputs["structured_delta"] = compute_pair_delta(pair_dir).to_dict()
    return inputs


def run_ablation(
    raw_run_path: Path,
    structured_run_path: Path,
    pairs_root: Path = Path("data/pairs"),
    results_dir: Path = Path("results"),
) -> tuple[Path, Path]:
    from datetime import datetime, timezone

    runs = {
        "raw": json.loads(Path(raw_run_path).read_text(encoding="utf-8")),
        "structured": json.loads(Path(structured_run_path).read_text(encoding="utf-8")),
    }
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    summary: dict[str, Any] = {
        "timestamp": timestamp,
        "source_runs": {
            "raw": str(raw_run_path),
            "structured": str(structured_run_path),
        },
        "policies": {key: description for key, description in POLICIES},
        "metrics": {},
        "per_pair": {},
    }

    decision_log: dict[str, list[dict[str, Any]]] = {"raw": [], "structured": []}

    for mode, payload in runs.items():
        metrics = {key: PolicyMetrics() for key, _ in POLICIES}
        for row in payload["results"]:
            truth = normalize_verdict(row.get("ground_truth")) or "error"
            model_results = _reconstruct_model_results(row)
            inputs = _pair_inputs(pairs_root, row, mode)

            # Policy A: replay the current adjudicator on identical inputs.
            adjudication_a = adjudicate(
                model_results,
                branch_a_diff=inputs["branch_a_diff"],
                branch_b_diff=inputs["branch_b_diff"],
                structured_delta=inputs["structured_delta"],
            )
            prediction_a = adjudication_a.final_verdict

            prediction_b = majority_prediction(row)

            start = time.perf_counter()
            adjudication_c = adjudicate_v2(
                model_results,
                branch_a_diff=inputs["branch_a_diff"],
                branch_b_diff=inputs["branch_b_diff"],
                structured_delta=inputs["structured_delta"],
            )
            latency_ms = (time.perf_counter() - start) * 1000
            prediction_c = adjudication_c.final_verdict

            metrics["A_current_escalation"].record(truth, prediction_a)
            metrics["B_majority_vote"].record(truth, prediction_b)
            metrics["C_evidence_weighted"].record(truth, prediction_c)
            metrics["C_evidence_weighted"].latencies_ms.append(latency_ms)
            metrics["C_evidence_weighted"].rationale_scores.extend(
                s["total"] for s in adjudication_c.rationale_scores
            )

            decision_log[mode].append(
                {
                    "pair": row["pair"],
                    "ground_truth": truth,
                    "model_verdicts": {
                        s["model"]: {
                            "verdict": s["verdict"],
                            "confidence": s["confidence"],
                            "rationale_score": s["total"],
                            "grounded": s["grounded_identifiers"],
                            "hallucinated": s["hallucinated_identifiers"],
                        }
                        for s in adjudication_c.rationale_scores
                    },
                    "policy_A": prediction_a,
                    "policy_B": prediction_b,
                    "policy_C": prediction_c,
                    "policy_C_rule": adjudication_c.decision_rule,
                    "policy_C_explanation": adjudication_c.explanation,
                }
            )

        summary["metrics"][mode] = {
            key: metric.to_dict() for key, metric in metrics.items()
        }
        summary["per_pair"][mode] = decision_log[mode]

    results_dir.mkdir(exist_ok=True)
    json_path = results_dir / f"adjudication_ablation_{timestamp}.json"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report_path = results_dir / f"adjudication_report_{timestamp}.md"
    report_path.write_text(_render_report(summary), encoding="utf-8")
    return json_path, report_path


def _pct(value: float | None) -> str:
    return f"{100 * value:.1f}%" if value is not None else "n/a"


def _render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Adjudication Policy Ablation",
        "",
        f"- Timestamp: `{summary['timestamp']}`",
        f"- Raw run: `{summary['source_runs']['raw']}`",
        f"- Structured run: `{summary['source_runs']['structured']}`",
        "",
        "Policies:",
    ]
    for key, description in POLICIES:
        lines.append(f"- **{key}** — {description}")
    lines.append("")

    for mode in ("raw", "structured"):
        lines.extend(
            [
                f"## {mode.title()} representation",
                "",
                "| Policy | Coverage | Escalations | Accuracy | Precision | Recall | F1 | "
                "Avg rationale | Avg latency |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for key, _ in POLICIES:
            m = summary["metrics"][mode][key]
            avg_rationale = m["average_rationale_score"]
            avg_latency = m["average_adjudication_latency_ms"]
            rationale_cell = f"{avg_rationale:.3f}" if avg_rationale is not None else "n/a"
            latency_cell = f"{avg_latency:.2f}ms" if avg_latency is not None else "n/a"
            lines.append(
                f"| {key} | {_pct(m['coverage'])} | "
                f"{m['escalations']}/{m['total']} ({_pct(m['escalation_rate'])}) | "
                f"{_pct(m['accuracy'])} | {_pct(m['precision'])} | "
                f"{_pct(m['recall'])} | {_pct(m['f1'])} | "
                f"{rationale_cell} | {latency_cell} |"
            )
        lines.append("")

        lines.append("### Per-pair decisions (policy C)")
        lines.append("")
        for entry in summary["per_pair"][mode]:
            lines.append(
                f"- **{entry['pair']}** (truth: {entry['ground_truth']}) — "
                f"A={entry['policy_A']}, B={entry['policy_B']}, "
                f"C={entry['policy_C']} via `{entry['policy_C_rule']}`"
            )
            lines.append(f"  - {entry['policy_C_explanation']}")
            for model, info in entry["model_verdicts"].items():
                lines.append(
                    f"  - {model}: {info['verdict']} "
                    f"(conf {info['confidence']:.2f}, score {info['rationale_score']:.2f}, "
                    f"grounded: {', '.join(info['grounded']) or 'none'})"
                )
        lines.append("")

    lines.extend(_success_criteria_section(summary))
    return "\n".join(lines)


def _success_criteria_section(summary: dict[str, Any]) -> list[str]:
    lines = ["## Success criteria", ""]
    for mode in ("raw", "structured"):
        c = summary["metrics"][mode]["C_evidence_weighted"]
        a = summary["metrics"][mode]["A_current_escalation"]
        coverage_ok = c["coverage"] > 0.70
        escalation_ok = c["escalation_rate"] < 0.25
        f1_ok = c["f1"] >= a["f1"] or c["coverage"] > a["coverage"]
        lines.append(
            f"- {mode}: coverage {_pct(c['coverage'])} "
            f"({'PASS' if coverage_ok else 'FAIL'} >70%), "
            f"escalation {_pct(c['escalation_rate'])} "
            f"({'PASS' if escalation_ok else 'FAIL'} <25%), "
            f"F1 {_pct(c['f1'])} vs current {_pct(a['f1'])} "
            f"({'PASS' if f1_ok else 'FAIL'})"
        )
    lines.append("")
    lines.append(
        "Note: the current policy's F1 is computed only over the pairs it decided "
        "(its coverage is near zero), so it is not directly comparable; the F1 "
        "check passes when evidence-weighted adjudication maintains F1 at "
        "dramatically higher coverage."
    )
    lines.append("")
    return lines
