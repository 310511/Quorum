"""Publication-ready statistical evaluation for Quorum.

Compares five systems on a labeled pair set using saved model outputs
(or freshly evaluated runs):

  A. Single-model baseline
  B. Majority vote
  C. Current (legacy) escalation policy
  D. Evidence-weighted committee (raw)
  E. Evidence-weighted committee + structured AST
"""

from __future__ import annotations

import json
import math
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from quorum.ablation import _reconstruct_model_results
from quorum.adjudicate import adjudicate
from quorum.adjudicate_v2 import adjudicate_v2, score_rationale, build_facts
from quorum.metrics import majority_prediction
from quorum.models import normalize_verdict

SYSTEMS = (
    ("A_baseline", "Single-model baseline"),
    ("B_majority_vote", "Majority vote"),
    ("C_legacy_escalation", "Current escalation policy"),
    ("D_evidence_weighted_raw", "Evidence-weighted committee (raw)"),
    ("E_evidence_weighted_structured", "Evidence-weighted + structured AST"),
)

ERROR_CATEGORIES = (
    "representation_error",
    "model_reasoning_error",
    "hallucinated_evidence",
    "adjudication_error",
    "dataset_ambiguity",
)


@dataclass
class Confusion:
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0
    escalate: int = 0
    error: int = 0
    correct: int = 0
    total: int = 0
    latencies: list[float] = field(default_factory=list)

    def record(self, truth: str, prediction: str, latency: float | None = None) -> None:
        self.total += 1
        if latency is not None:
            self.latencies.append(latency)
        if prediction == "escalate":
            self.escalate += 1
            return
        if prediction not in ("conflict", "no_conflict"):
            self.error += 1
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

    def metrics(self) -> dict[str, Any]:
        decided = self.tp + self.fp + self.tn + self.fn
        precision = self.tp / (self.tp + self.fp) if self.tp + self.fp else 0.0
        recall = self.tp / (self.tp + self.fn) if self.tp + self.fn else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )
        return {
            "n": self.total,
            "accuracy": self.correct / self.total if self.total else 0.0,
            "decided_accuracy": self.correct / decided if decided else 0.0,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "coverage": decided / self.total if self.total else 0.0,
            "escalation_rate": self.escalate / self.total if self.total else 0.0,
            "escalations": self.escalate,
            "errors": self.error,
            "latency_mean_s": (
                sum(self.latencies) / len(self.latencies) if self.latencies else None
            ),
            "confusion_matrix": {
                "tp": self.tp,
                "fp": self.fp,
                "tn": self.tn,
                "fn": self.fn,
                "escalate": self.escalate,
                "error": self.error,
            },
        }


def _wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)
    return (max(0.0, (centre - margin) / denom), min(1.0, (centre + margin) / denom))


def _metric_ci(values: list[float], n_boot: int = 2000, seed: int = 0) -> dict[str, float]:
    """Bootstrap percentile CI for a mean of per-example 0/1 or continuous scores."""
    if not values:
        return {"mean": 0.0, "ci95_low": 0.0, "ci95_high": 0.0}
    # Deterministic LCG bootstrap without numpy dependency.
    state = seed & 0xFFFFFFFF
    n = len(values)
    means: list[float] = []
    for _ in range(n_boot):
        total = 0.0
        for _ in range(n):
            state = (1664525 * state + 1013904223) & 0xFFFFFFFF
            idx = state % n
            total += values[idx]
        means.append(total / n)
    means.sort()
    lo = means[int(0.025 * (n_boot - 1))]
    hi = means[int(0.975 * (n_boot - 1))]
    return {"mean": sum(values) / n, "ci95_low": lo, "ci95_high": hi}


def mcnemar_test(pred_a: list[str], pred_b: list[str], truth: list[str]) -> dict[str, Any]:
    """McNemar's test on paired correctness (decided predictions only).

    Continuity-corrected statistic; p-value via chi-square survival with 1 df.
    Cases where either system escalates/errors are excluded from the contingency.
    """
    b01 = 0  # A wrong, B correct
    b10 = 0  # A correct, B wrong
    for a, b, t in zip(pred_a, pred_b, truth):
        if a not in ("conflict", "no_conflict") or b not in ("conflict", "no_conflict"):
            continue
        a_ok = a == t
        b_ok = b == t
        if a_ok and not b_ok:
            b10 += 1
        elif b_ok and not a_ok:
            b01 += 1
    n = b01 + b10
    if n == 0:
        return {
            "b01": b01,
            "b10": b10,
            "statistic": 0.0,
            "p_value": 1.0,
            "n_discordant": 0,
        }
    # Edwards continuity correction
    stat = (abs(b01 - b10) - 1) ** 2 / n
    # chi-square df=1 survival: erfc(sqrt(x/2)/sqrt(2)) wait — P(X>x) = erfc(sqrt(x/2))
    p = math.erfc(math.sqrt(stat / 2.0))
    return {
        "b01": b01,
        "b10": b10,
        "statistic": stat,
        "p_value": p,
        "n_discordant": n,
    }


def _pair_inputs(pairs_root: Path, pair_name: str, mode: str) -> dict[str, Any]:
    pair_dir = pairs_root / pair_name
    if not pair_dir.exists():
        # hard_benchmark nests under hard_benchmark/
        alt = pairs_root / "hard_benchmark" / pair_name
        if alt.exists():
            pair_dir = alt
        else:
            # search one level
            matches = list(pairs_root.glob(f"**/{pair_name}"))
            if matches:
                pair_dir = matches[0]
    branch_a = pair_dir / "branch_a.diff"
    branch_b = pair_dir / "branch_b.diff"
    inputs: dict[str, Any] = {
        "pair_dir": pair_dir,
        "branch_a_diff": branch_a.read_text(encoding="utf-8") if branch_a.exists() else "",
        "branch_b_diff": branch_b.read_text(encoding="utf-8") if branch_b.exists() else "",
        "structured_delta": None,
    }
    if mode == "structured" and pair_dir.exists():
        from quorum.delta import compute_pair_delta

        inputs["structured_delta"] = compute_pair_delta(pair_dir).to_dict()
    return inputs


def _latency(row: dict[str, Any], system: str) -> float:
    if system == "A_baseline":
        return float(row["baseline"]["wall_clock_seconds"])
    return float(row["committee"]["wall_clock_seconds"])


def predict_systems(
    raw_row: dict[str, Any],
    structured_row: dict[str, Any] | None,
    pairs_root: Path,
) -> dict[str, Any]:
    """Produce predictions for systems A–E for one pair."""
    truth = normalize_verdict(raw_row.get("ground_truth")) or "error"
    model_results_raw = _reconstruct_model_results(raw_row)
    inputs_raw = _pair_inputs(pairs_root, raw_row["pair"], "raw")

    legacy = adjudicate(
        model_results_raw,
        branch_a_diff=inputs_raw["branch_a_diff"],
        branch_b_diff=inputs_raw["branch_b_diff"],
    )
    evidence_raw = adjudicate_v2(
        model_results_raw,
        branch_a_diff=inputs_raw["branch_a_diff"],
        branch_b_diff=inputs_raw["branch_b_diff"],
    )

    predictions = {
        "A_baseline": normalize_verdict(raw_row.get("baseline_verdict")) or "error",
        "B_majority_vote": majority_prediction(raw_row),
        "C_legacy_escalation": legacy.final_verdict,
        "D_evidence_weighted_raw": evidence_raw.final_verdict,
    }
    details = {
        "truth": truth,
        "D_rule": evidence_raw.decision_rule,
        "D_explanation": evidence_raw.explanation,
        "D_scores": evidence_raw.rationale_scores,
        "latencies": {
            "A_baseline": _latency(raw_row, "A_baseline"),
            "B_majority_vote": _latency(raw_row, "B_majority_vote"),
            "C_legacy_escalation": _latency(raw_row, "C_legacy_escalation"),
            "D_evidence_weighted_raw": _latency(raw_row, "D_evidence_weighted_raw"),
        },
    }

    if structured_row is not None:
        model_results_s = _reconstruct_model_results(structured_row)
        inputs_s = _pair_inputs(pairs_root, structured_row["pair"], "structured")
        evidence_s = adjudicate_v2(
            model_results_s,
            branch_a_diff=inputs_s["branch_a_diff"],
            branch_b_diff=inputs_s["branch_b_diff"],
            structured_delta=inputs_s["structured_delta"],
        )
        predictions["E_evidence_weighted_structured"] = evidence_s.final_verdict
        details["E_rule"] = evidence_s.decision_rule
        details["E_explanation"] = evidence_s.explanation
        details["E_scores"] = evidence_s.rationale_scores
        details["latencies"]["E_evidence_weighted_structured"] = _latency(
            structured_row, "E_evidence_weighted_structured"
        )
    else:
        predictions["E_evidence_weighted_structured"] = "error"
        details["E_rule"] = "missing_structured_run"
        details["E_explanation"] = "No structured evaluation row for this pair."
        details["E_scores"] = []
        details["latencies"]["E_evidence_weighted_structured"] = None

    return {"pair": raw_row["pair"], "predictions": predictions, "details": details}


def categorize_error(
    *,
    truth: str,
    prediction: str,
    system: str,
    raw_row: dict[str, Any],
    structured_row: dict[str, Any] | None,
    details: dict[str, Any],
) -> str | None:
    """Assign a single primary error category for an incorrect decided prediction."""
    if prediction in ("escalate", "error") or prediction == truth:
        return None

    # Dataset ambiguity first: models unanimously agree with each other but
    # disagree with the label — likely a hard/noisy label rather than a system bug.
    votes = []
    for result in raw_row["committee"]["model_results"]:
        if result.get("outcome") == "ok" and result.get("verdict"):
            votes.append(normalize_verdict(result["verdict"].get("verdict")))
    if votes and len(set(votes)) == 1 and votes[0] == prediction and prediction != truth:
        return "dataset_ambiguity"

    scores = details.get("D_scores") or []
    if system == "E_evidence_weighted_structured":
        scores = details.get("E_scores") or scores

    hallucinated = any(s.get("hallucinated_identifiers") for s in scores)
    grounded_weak = all((s.get("total") or 0) < 0.25 for s in scores) if scores else False

    if hallucinated and prediction != truth:
        return "hallucinated_evidence"

    # Representation: raw wrong, structured correct (or vice versa for D vs E)
    if system == "D_evidence_weighted_raw" and structured_row is not None:
        e_pred = details.get("_E_pred")
        if e_pred == truth and prediction != truth:
            return "representation_error"

    if system == "E_evidence_weighted_structured":
        d_pred = details.get("_D_pred")
        if d_pred == truth and prediction != truth:
            return "representation_error"

    # Adjudication: majority correct but this committee policy wrong
    maj = majority_prediction(raw_row)
    if system in {
        "C_legacy_escalation",
        "D_evidence_weighted_raw",
        "E_evidence_weighted_structured",
    }:
        if maj == truth and prediction != truth:
            return "adjudication_error"

    if grounded_weak:
        return "model_reasoning_error"

    return "model_reasoning_error"


def evaluate_publication(
    *,
    raw_results: list[dict[str, Any]],
    structured_by_pair: dict[str, dict[str, Any]],
    pairs_root: Path,
    corpus_name: str,
) -> dict[str, Any]:
    confusions = {key: Confusion() for key, _ in SYSTEMS}
    per_pair: list[dict[str, Any]] = []
    per_example_scores: dict[str, dict[str, list[float]]] = {
        key: {"accuracy": [], "precision_support": [], "recall_support": []}
        for key, _ in SYSTEMS
    }
    # For bootstrap of precision/recall we track per-example contributions carefully later.
    predictions_by_system: dict[str, list[str]] = {key: [] for key, _ in SYSTEMS}
    truths: list[str] = []
    error_rows: list[dict[str, Any]] = []

    for raw_row in raw_results:
        structured_row = structured_by_pair.get(raw_row["pair"])
        outcome = predict_systems(raw_row, structured_row, pairs_root)
        truth = outcome["details"]["truth"]
        truths.append(truth)
        outcome["details"]["_D_pred"] = outcome["predictions"]["D_evidence_weighted_raw"]
        outcome["details"]["_E_pred"] = outcome["predictions"]["E_evidence_weighted_structured"]

        pair_entry = {
            "pair": raw_row["pair"],
            "ground_truth": truth,
            "corpus": corpus_name,
            "predictions": outcome["predictions"],
            "decision_rules": {
                "D": outcome["details"].get("D_rule"),
                "E": outcome["details"].get("E_rule"),
            },
            "explanations": {
                "D": outcome["details"].get("D_explanation"),
                "E": outcome["details"].get("E_explanation"),
            },
            "errors": {},
        }

        for system, _ in SYSTEMS:
            pred = outcome["predictions"][system]
            predictions_by_system[system].append(pred)
            latency = outcome["details"]["latencies"].get(system)
            confusions[system].record(truth, pred, latency)
            # accuracy indicator for bootstrap
            if pred in ("conflict", "no_conflict"):
                per_example_scores[system]["accuracy"].append(1.0 if pred == truth else 0.0)
            else:
                per_example_scores[system]["accuracy"].append(0.0)

            if pred in ("conflict", "no_conflict") and pred != truth:
                category = categorize_error(
                    truth=truth,
                    prediction=pred,
                    system=system,
                    raw_row=raw_row,
                    structured_row=structured_row,
                    details=outcome["details"],
                )
                pair_entry["errors"][system] = {
                    "prediction": pred,
                    "category": category,
                }
                error_rows.append(
                    {
                        "pair": raw_row["pair"],
                        "corpus": corpus_name,
                        "system": system,
                        "truth": truth,
                        "prediction": pred,
                        "category": category,
                    }
                )

        per_pair.append(pair_entry)

    # Aggregate metrics + CIs
    system_tables: dict[str, Any] = {}
    for system, description in SYSTEMS:
        m = confusions[system].metrics()
        acc_ci = _wilson_ci(confusions[system].correct, confusions[system].total)
        tp, fp, fn = (
            confusions[system].tp,
            confusions[system].fp,
            confusions[system].fn,
        )
        prec_ci = _wilson_ci(tp, tp + fp) if tp + fp else (0.0, 0.0)
        rec_ci = _wilson_ci(tp, tp + fn) if tp + fn else (0.0, 0.0)
        system_tables[system] = {
            "description": description,
            **m,
            "accuracy_ci95": list(acc_ci),
            "precision_ci95": list(prec_ci),
            "recall_ci95": list(rec_ci),
            "f1_ci95": _f1_ci(tp, fp, fn),
        }

    # Pairwise McNemar (all system pairs)
    significance: dict[str, Any] = {}
    keys = [k for k, _ in SYSTEMS]
    for i, a in enumerate(keys):
        for b in keys[i + 1 :]:
            significance[f"{a}_vs_{b}"] = mcnemar_test(
                predictions_by_system[a],
                predictions_by_system[b],
                truths,
            )

    error_summary = Counter(row["category"] for row in error_rows if row["category"])
    error_by_system: dict[str, Counter] = defaultdict(Counter)
    for row in error_rows:
        if row["category"]:
            error_by_system[row["system"]][row["category"]] += 1

    return {
        "corpus": corpus_name,
        "n_pairs": len(raw_results),
        "label_distribution": dict(Counter(truths)),
        "systems": system_tables,
        "significance": significance,
        "error_analysis": {
            "counts": dict(error_summary),
            "by_system": {k: dict(v) for k, v in error_by_system.items()},
            "rows": error_rows,
        },
        "per_pair": per_pair,
    }


def _f1_ci(tp: int, fp: int, fn: int, n_boot: int = 2000, seed: int = 7) -> list[float]:
    """Bootstrap F1 over a reconstructed list of (truth, pred) conflict-class decisions."""
    examples: list[tuple[str, str]] = []
    examples.extend([("conflict", "conflict")] * tp)
    examples.extend([("no_conflict", "conflict")] * fp)
    examples.extend([("conflict", "no_conflict")] * fn)
    # tn does not affect P/R/F1 for positive=conflict
    if not examples:
        return [0.0, 0.0]
    state = seed & 0xFFFFFFFF
    n = len(examples)
    scores: list[float] = []
    for _ in range(n_boot):
        tp_b = fp_b = fn_b = 0
        for _ in range(n):
            state = (1664525 * state + 1013904223) & 0xFFFFFFFF
            t, p = examples[state % n]
            if t == "conflict" and p == "conflict":
                tp_b += 1
            elif t == "no_conflict" and p == "conflict":
                fp_b += 1
            elif t == "conflict" and p == "no_conflict":
                fn_b += 1
        prec = tp_b / (tp_b + fp_b) if tp_b + fp_b else 0.0
        rec = tp_b / (tp_b + fn_b) if tp_b + fn_b else 0.0
        scores.append(
            2 * prec * rec / (prec + rec) if prec + rec else 0.0
        )
    scores.sort()
    return [scores[int(0.025 * (n_boot - 1))], scores[int(0.975 * (n_boot - 1))]]


def merge_corpus_results(parts: list[dict[str, Any]]) -> dict[str, Any]:
    """Recompute metrics over concatenated per-pair rows from multiple corpora."""
    # Rebuild from per_pair predictions without re-adjudicating.
    confusions = {key: Confusion() for key, _ in SYSTEMS}
    predictions_by_system: dict[str, list[str]] = {key: [] for key, _ in SYSTEMS}
    truths: list[str] = []
    error_rows: list[dict[str, Any]] = []
    per_pair: list[dict[str, Any]] = []
    acc_values: dict[str, list[float]] = {key: [] for key, _ in SYSTEMS}

    for part in parts:
        for entry in part["per_pair"]:
            truth = entry["ground_truth"]
            truths.append(truth)
            per_pair.append(entry)
            for system, _ in SYSTEMS:
                pred = entry["predictions"][system]
                predictions_by_system[system].append(pred)
                confusions[system].record(truth, pred)
                acc_values[system].append(
                    1.0 if pred == truth and pred in ("conflict", "no_conflict") else 0.0
                )
            for system, err in entry.get("errors", {}).items():
                error_rows.append(
                    {
                        "pair": entry["pair"],
                        "corpus": entry.get("corpus"),
                        "system": system,
                        "truth": truth,
                        "prediction": err["prediction"],
                        "category": err["category"],
                    }
                )
            # recover latencies if present in original parts' system tables only as means —
            # skip per-example latency in merged unless we stored them.

    system_tables: dict[str, Any] = {}
    for system, description in SYSTEMS:
        m = confusions[system].metrics()
        # Carry forward mean latency from parts (weighted by n)
        lat_num = lat_den = 0.0
        for part in parts:
            sm = part["systems"][system]
            if sm.get("latency_mean_s") is not None:
                lat_num += sm["latency_mean_s"] * sm["n"]
                lat_den += sm["n"]
        m["latency_mean_s"] = lat_num / lat_den if lat_den else None
        tp, fp, fn = confusions[system].tp, confusions[system].fp, confusions[system].fn
        acc_ci = _wilson_ci(confusions[system].correct, confusions[system].total)
        system_tables[system] = {
            "description": description,
            **m,
            "accuracy_ci95": list(acc_ci),
            "precision_ci95": list(_wilson_ci(tp, tp + fp) if tp + fp else (0.0, 0.0)),
            "recall_ci95": list(_wilson_ci(tp, tp + fn) if tp + fn else (0.0, 0.0)),
            "f1_ci95": _f1_ci(tp, fp, fn),
        }

    significance: dict[str, Any] = {}
    keys = [k for k, _ in SYSTEMS]
    for i, a in enumerate(keys):
        for b in keys[i + 1 :]:
            significance[f"{a}_vs_{b}"] = mcnemar_test(
                predictions_by_system[a],
                predictions_by_system[b],
                truths,
            )

    error_summary = Counter(r["category"] for r in error_rows if r["category"])
    error_by_system: dict[str, Counter] = defaultdict(Counter)
    for row in error_rows:
        if row["category"]:
            error_by_system[row["system"]][row["category"]] += 1

    return {
        "corpus": "combined",
        "n_pairs": len(per_pair),
        "label_distribution": dict(Counter(truths)),
        "systems": system_tables,
        "significance": significance,
        "error_analysis": {
            "counts": dict(error_summary),
            "by_system": {k: dict(v) for k, v in error_by_system.items()},
            "rows": error_rows,
        },
        "per_pair": per_pair,
        "parts": [p["corpus"] for p in parts],
    }


def render_markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Quorum Publication Evaluation",
        "",
        f"- Generated: `{payload['timestamp']}`",
        f"- Combined N: **{payload['combined']['n_pairs']}**",
        f"- Label distribution: `{payload['combined']['label_distribution']}`",
        "",
        "## Systems",
        "",
    ]
    for key, desc in SYSTEMS:
        lines.append(f"- **{key}** — {desc}")
    lines.extend(["", "## Main results (combined)", ""])
    lines.append(
        "| System | Acc | Acc 95% CI | P | R | F1 | F1 95% CI | Coverage | Escalation | Latency |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for key, _ in SYSTEMS:
        s = payload["combined"]["systems"][key]
        lat = s["latency_mean_s"]
        lat_s = f"{lat:.1f}s" if lat is not None else "n/a"
        lines.append(
            f"| {key} | {_pct(s['accuracy'])} | "
            f"[{_pct(s['accuracy_ci95'][0])}, {_pct(s['accuracy_ci95'][1])}] | "
            f"{_pct(s['precision'])} | {_pct(s['recall'])} | {_pct(s['f1'])} | "
            f"[{_pct(s['f1_ci95'][0])}, {_pct(s['f1_ci95'][1])}] | "
            f"{_pct(s['coverage'])} | {_pct(s['escalation_rate'])} | {lat_s} |"
        )

    lines.extend(["", "## McNemar paired significance", ""])
    lines.append("| Comparison | b01 | b10 | χ² | p-value |")
    lines.append("|---|---:|---:|---:|---:|")
    for name, stats in payload["combined"]["significance"].items():
        lines.append(
            f"| {name} | {stats['b01']} | {stats['b10']} | "
            f"{stats['statistic']:.3f} | {stats['p_value']:.4g} |"
        )

    lines.extend(["", "## Error analysis", ""])
    lines.append("| Category | Count |")
    lines.append("|---|---:|")
    for cat in ERROR_CATEGORIES:
        count = payload["combined"]["error_analysis"]["counts"].get(cat, 0)
        lines.append(f"| {cat} | {count} |")

    lines.extend(["", "### Errors by system", ""])
    for system, _ in SYSTEMS:
        by = payload["combined"]["error_analysis"]["by_system"].get(system, {})
        if not by:
            continue
        lines.append(f"- **{system}**: " + ", ".join(f"{k}={v}" for k, v in sorted(by.items())))

    for corpus_key in ("cooperbench_python", "hard_benchmark"):
        if corpus_key not in payload:
            continue
        part = payload[corpus_key]
        lines.extend(["", f"## Corpus: {corpus_key} (N={part['n_pairs']})", ""])
        lines.append("| System | Acc | P | R | F1 | Coverage | Escalation |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        for key, _ in SYSTEMS:
            s = part["systems"][key]
            lines.append(
                f"| {key} | {_pct(s['accuracy'])} | {_pct(s['precision'])} | "
                f"{_pct(s['recall'])} | {_pct(s['f1'])} | {_pct(s['coverage'])} | "
                f"{_pct(s['escalation_rate'])} |"
            )

    lines.extend(["", "## Per-pair decision log (abbreviated)", ""])
    for entry in payload["combined"]["per_pair"]:
        preds = entry["predictions"]
        lines.append(
            f"- `{entry['pair']}` truth={entry['ground_truth']} "
            f"A={preds['A_baseline']} B={preds['B_majority_vote']} "
            f"C={preds['C_legacy_escalation']} D={preds['D_evidence_weighted_raw']} "
            f"E={preds['E_evidence_weighted_structured']}"
        )
        if entry.get("errors"):
            for sys, err in entry["errors"].items():
                lines.append(f"  - error/{sys}: {err['prediction']} → {err['category']}")

    return "\n".join(lines) + "\n"


def _pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{100 * value:.1f}%"


def write_latex_tables(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "% Auto-generated Quorum publication tables",
        "\\begin{table}[t]",
        "\\centering",
        "\\small",
        "\\caption{Five-system comparison on the combined Quorum benchmark.}",
        "\\label{tab:main-results}",
        "\\begin{tabular}{lccccccc}",
        "\\toprule",
        "System & Acc & P & R & F1 & Cov. & Esc. & Lat. \\\\",
        "\\midrule",
    ]
    short = {
        "A_baseline": "A Baseline",
        "B_majority_vote": "B Majority",
        "C_legacy_escalation": "C Legacy esc.",
        "D_evidence_weighted_raw": "D Evid. (raw)",
        "E_evidence_weighted_structured": "E Evid.+AST",
    }
    for key, _ in SYSTEMS:
        s = payload["combined"]["systems"][key]
        lat = s["latency_mean_s"]
        lat_s = f"{lat:.1f}s" if lat is not None else "--"
        lines.append(
            f"{short[key]} & {_pct(s['accuracy'])} & {_pct(s['precision'])} & "
            f"{_pct(s['recall'])} & {_pct(s['f1'])} & {_pct(s['coverage'])} & "
            f"{_pct(s['escalation_rate'])} & {lat_s} \\\\"
        )
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\end{table}",
            "",
            "\\begin{table}[t]",
            "\\centering",
            "\\small",
            "\\caption{Error taxonomy on incorrect decided predictions.}",
            "\\label{tab:error-analysis}",
            "\\begin{tabular}{lr}",
            "\\toprule",
            "Category & Count \\\\",
            "\\midrule",
        ]
    )
    for cat in ERROR_CATEGORIES:
        count = payload["combined"]["error_analysis"]["counts"].get(cat, 0)
        lines.append(f"{cat.replace('_', ' ')} & {count} \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_figures(payload: dict[str, Any], fig_dir: Path) -> list[Path]:
    """Write SVG figures (no matplotlib dependency)."""
    fig_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    # Figure 1: grouped bars for Acc/F1/Coverage/Escalation
    metrics = ["accuracy", "f1", "coverage", "escalation_rate"]
    labels = ["Accuracy", "F1", "Coverage", "Escalation"]
    systems = [k for k, _ in SYSTEMS]
    short = ["A", "B", "C", "D", "E"]
    width, height = 720, 360
    chart = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="24" y="28" font-family="Georgia, serif" font-size="16">Quorum five-system comparison</text>',
    ]
    colors = ["#1f4e5f", "#079187", "#c45c26", "#3d5a80", "#9b2226"]
    group_w = 140
    bar_w = 22
    origin_y = 300
    max_h = 220
    for mi, metric in enumerate(metrics):
        gx = 50 + mi * group_w
        chart.append(
            f'<text x="{gx + 40}" y="330" font-family="Helvetica, sans-serif" font-size="11" text-anchor="middle">{labels[mi]}</text>'
        )
        for si, system in enumerate(systems):
            val = payload["combined"]["systems"][system][metric]
            h = max_h * val
            x = gx + si * (bar_w + 2)
            y = origin_y - h
            chart.append(
                f'<rect x="{x}" y="{y}" width="{bar_w}" height="{h}" fill="{colors[si]}"/>'
            )
    for si, name in enumerate(short):
        chart.append(
            f'<rect x="{50 + si * 50}" y="345" width="12" height="12" fill="{colors[si]}"/>'
            f'<text x="{66 + si * 50}" y="355" font-family="Helvetica, sans-serif" font-size="11">{name}</text>'
        )
    chart.append("</svg>")
    path1 = fig_dir / "fig1_main_metrics.svg"
    path1.write_text("\n".join(chart), encoding="utf-8")
    written.append(path1)

    # Figure 2: error taxonomy pie-like horizontal bars
    counts = payload["combined"]["error_analysis"]["counts"]
    total = sum(counts.get(c, 0) for c in ERROR_CATEGORIES) or 1
    chart2 = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="280">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="24" y="28" font-family="Georgia, serif" font-size="16">Error taxonomy</text>',
    ]
    for i, cat in enumerate(ERROR_CATEGORIES):
        c = counts.get(cat, 0)
        y = 50 + i * 40
        w = 400 * (c / total)
        chart2.append(f'<text x="24" y="{y + 14}" font-family="Helvetica, sans-serif" font-size="12">{cat.replace("_", " ")}</text>')
        chart2.append(f'<rect x="200" y="{y}" width="{w}" height="18" fill="#1f4e5f"/>')
        chart2.append(
            f'<text x="{210 + w}" y="{y + 14}" font-family="Helvetica, sans-serif" font-size="12">{c}</text>'
        )
    chart2.append("</svg>")
    path2 = fig_dir / "fig2_error_taxonomy.svg"
    path2.write_text("\n".join(chart2), encoding="utf-8")
    written.append(path2)

    # Figure 3: coverage vs escalation scatter-ish bars for C vs D vs E
    chart3 = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="560" height="300">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="24" y="28" font-family="Georgia, serif" font-size="16">Coverage vs escalation (C/D/E)</text>',
    ]
    for i, system in enumerate(
        ["C_legacy_escalation", "D_evidence_weighted_raw", "E_evidence_weighted_structured"]
    ):
        s = payload["combined"]["systems"][system]
        x = 80 + i * 150
        cov_h = 200 * s["coverage"]
        esc_h = 200 * s["escalation_rate"]
        chart3.append(f'<rect x="{x}" y="{250 - cov_h}" width="40" height="{cov_h}" fill="#079187"/>')
        chart3.append(f'<rect x="{x + 45}" y="{250 - esc_h}" width="40" height="{esc_h}" fill="#c45c26"/>')
        chart3.append(
            f'<text x="{x + 40}" y="270" text-anchor="middle" font-family="Helvetica, sans-serif" font-size="12">{system[0]}</text>'
        )
    chart3.append('<rect x="80" y="285" width="12" height="12" fill="#079187"/><text x="96" y="295" font-size="11" font-family="Helvetica,sans-serif">Coverage</text>')
    chart3.append('<rect x="180" y="285" width="12" height="12" fill="#c45c26"/><text x="196" y="295" font-size="11" font-family="Helvetica,sans-serif">Escalation</text>')
    chart3.append("</svg>")
    path3 = fig_dir / "fig3_coverage_escalation.svg"
    path3.write_text("\n".join(chart3), encoding="utf-8")
    written.append(path3)

    return written


def run_publication_pipeline(
    *,
    cooper_raw: Path,
    cooper_structured: Path,
    hard_raw: Path | None,
    hard_structured: Path | None,
    pairs_root: Path,
    results_dir: Path,
) -> dict[str, Path]:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    cooper_raw_data = json.loads(Path(cooper_raw).read_text(encoding="utf-8"))
    cooper_struct_data = json.loads(Path(cooper_structured).read_text(encoding="utf-8"))
    cooper_struct_map = {r["pair"]: r for r in cooper_struct_data["results"]}

    cooper_eval = evaluate_publication(
        raw_results=cooper_raw_data["results"],
        structured_by_pair=cooper_struct_map,
        pairs_root=pairs_root,
        corpus_name="cooperbench_python",
    )

    parts = [cooper_eval]
    payload: dict[str, Any] = {
        "timestamp": timestamp,
        "source_runs": {
            "cooper_raw": str(cooper_raw),
            "cooper_structured": str(cooper_structured),
            "hard_raw": str(hard_raw) if hard_raw else None,
            "hard_structured": str(hard_structured) if hard_structured else None,
        },
        "cooperbench_python": cooper_eval,
    }

    if hard_raw and Path(hard_raw).exists():
        hard_raw_data = json.loads(Path(hard_raw).read_text(encoding="utf-8"))
        hard_struct_map: dict[str, dict] = {}
        if hard_structured and Path(hard_structured).exists():
            hard_struct_data = json.loads(Path(hard_structured).read_text(encoding="utf-8"))
            hard_struct_map = {r["pair"]: r for r in hard_struct_data["results"]}
        # Resolve pairs root for hard pairs
        hard_pairs_root = pairs_root / "hard_benchmark"
        if not hard_pairs_root.exists():
            hard_pairs_root = pairs_root
        hard_eval = evaluate_publication(
            raw_results=hard_raw_data["results"],
            structured_by_pair=hard_struct_map,
            pairs_root=hard_pairs_root,
            corpus_name="hard_benchmark",
        )
        payload["hard_benchmark"] = hard_eval
        parts.append(hard_eval)

    payload["combined"] = merge_corpus_results(parts)

    results_dir.mkdir(parents=True, exist_ok=True)
    out_json = results_dir / f"publication_eval_{timestamp}.json"
    out_md = results_dir / f"publication_report_{timestamp}.md"
    out_tex = results_dir / f"publication_tables_{timestamp}.tex"
    fig_dir = results_dir / f"publication_figures_{timestamp}"

    # Strip bulky per-pair from disk? Keep it — needed for paper appendix.
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    out_md.write_text(render_markdown_report(payload), encoding="utf-8")
    write_latex_tables(payload, out_tex)
    figs = write_figures(payload, fig_dir)

    return {
        "json": out_json,
        "markdown": out_md,
        "latex": out_tex,
        "figures": fig_dir,
        "figure_files": figs,
    }
