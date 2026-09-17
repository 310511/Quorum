"""Phase 6: conflict heuristics (estimated labels only — never ground truth)."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

from real_world.common import append_jsonl, load_existing_ids, progress, read_jsonl, write_jsonl
from real_world.config import CLASSIFIED_JSONL, HEURISTICS_JSONL, REPO_BY_SLUG
from real_world.filters.initial_filter import diff_text

logger = logging.getLogger(__name__)


@dataclass
class HeuristicResult:
    estimated_label: str  # conflict | compatible | uncertain
    confidence: float
    reason: str
    indicators: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "estimated_label": self.estimated_label,
            "confidence": self.confidence,
            "reason": self.reason,
            "indicators": self.indicators,
        }


def _indicators_from_diffs(left_diff: str, right_diff: str, symbols: list[str]) -> list[tuple[str, float, str]]:
    hits: list[tuple[str, float, str]] = []
    combined = left_diff + "\n" + right_diff
    symbol_names = {s.split(".")[-1] for s in symbols}

    if re.search(r"def\s+\w+\([^)]*\)", combined) and re.search(r"\b\w+\(", combined):
        for name in symbol_names:
            if re.search(rf"def\s+{re.escape(name)}\(", combined) and re.search(
                rf"\b{re.escape(name)}\(", combined
            ):
                hits.append(
                    (
                        "signature_change_with_stale_caller",
                        0.72,
                        f"Function `{name}` signature/body changed while still referenced",
                    )
                )

    if re.search(r"->\s*\w+", combined) and re.search(r"=\s*\w+\(", combined):
        hits.append(("return_type_with_caller_dependency", 0.65, "Return annotation change near call sites"))

    if re.search(r"raise \w+", combined) and re.search(r"except \w+", combined):
        hits.append(("exception_contract_shift", 0.68, "Exception raise/handler mismatch suspected"))

    if re.search(r"self\.\w+\s*=", combined) and len(symbol_names) >= 2:
        hits.append(("shared_state_mutation", 0.60, "Both branches touch shared object state"))

    if re.search(r"Field\(|validator|validate", combined, re.I):
        hits.append(("validation_rule_change", 0.63, "Validation logic changed with dependent usage"))

    if re.search(r"Depends\(|APIRouter|@app\.", combined):
        hits.append(("dependency_injection_or_routing", 0.58, "DI/routing surface changed"))

    if re.search(r"Column\(|relationship\(|ForeignKey", combined):
        hits.append(("orm_model_query_drift", 0.70, "ORM model/query semantics may diverge"))

    if re.search(r"commit\(|rollback|atomic\(", combined):
        hits.append(("transaction_behavior", 0.67, "Transaction boundary behavior changed"))

    if re.search(r"__enter__|close\(|dispose\(", combined):
        hits.append(("resource_ownership", 0.62, "Resource ownership/lifetime change"))

    if re.search(r"async def", combined) and re.search(r"await ", combined):
        hits.append(("async_contract", 0.55, "Async/sync contract may be incompatible"))

    # Compatible signals: orthogonal additions in different symbols/files.
    left_defs = set(re.findall(r"^\+def (\w+)", left_diff, re.M))
    right_defs = set(re.findall(r"^\+def (\w+)", right_diff, re.M))
    if left_defs and right_defs and not (left_defs & right_defs):
        if not any(name in right_diff for name in left_defs) and not any(
            name in left_diff for name in right_defs
        ):
            hits.append(
                (
                    "orthogonal_function_additions",
                    0.55,
                    "Branches add different functions without cross references",
                )
            )

    return hits


def score_heuristics(record: dict[str, Any]) -> dict[str, Any]:
    spec = REPO_BY_SLUG[record["repository"]]
    repo = spec.clone_path
    merge_base = record["merge_base"]
    parent_a = record["parent_a"]
    parent_b = record["parent_b"]
    left_diff = diff_text(repo, merge_base, parent_a)
    right_diff = diff_text(repo, merge_base, parent_b)
    symbols = record.get("affected_symbols") or record.get("intersection", {}).get(
        "shared_symbols", []
    )

    hits = _indicators_from_diffs(left_diff, right_diff, symbols)
    conflict_score = sum(score for name, score, _ in hits if "orthogonal" not in name)
    compatible_score = sum(score for name, score, _ in hits if "orthogonal" in name)

    if conflict_score >= 0.65 and conflict_score > compatible_score + 0.1:
        result = HeuristicResult(
            estimated_label="conflict",
            confidence=min(0.95, conflict_score),
            reason=hits[0][2] if hits else "Multiple conflict indicators",
            indicators=[h[0] for h in hits],
        )
    elif compatible_score >= 0.5 and compatible_score > conflict_score:
        result = HeuristicResult(
            estimated_label="compatible",
            confidence=min(0.85, compatible_score),
            reason="Branches appear orthogonal with weak conflict signals",
            indicators=[h[0] for h in hits],
        )
    else:
        result = HeuristicResult(
            estimated_label="uncertain",
            confidence=0.35,
            reason="Insufficient heuristic evidence for automatic estimate",
            indicators=[h[0] for h in hits],
        )

    return {**record, "heuristic": result.to_dict()}


def run_heuristics(*, resume: bool = True) -> dict[str, int]:
    records = read_jsonl(CLASSIFIED_JSONL)
    existing = load_existing_ids(HEURISTICS_JSONL) if resume else set()
    output: list[dict[str, Any]] = []
    kept = 0

    for record in progress(records, desc="heuristics", total=len(records)):
        if resume and record["id"] in existing:
            continue
        scored = score_heuristics(record)
        append_jsonl(HEURISTICS_JSONL, scored)
        output.append(scored)
        kept += 1

    if not resume:
        write_jsonl(HEURISTICS_JSONL, [score_heuristics(r) for r in records])
        kept = len(records)

    logger.info("Scored heuristics for %d candidates", kept)
    return {"scored": kept}
