"""Evidence-weighted adjudication: score rationales, don't just count votes."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from quorum.adjudicate import extract_identifiers
from quorum.models import ModelResult

FinalOutcome = str  # "conflict" | "no_conflict" | "escalate"

# Decision thresholds
DOMINANCE_MARGIN = 0.12   # best rationale must beat the other side by this much
WEIGHT_EPSILON = 0.05     # weighted-vote tie band
LOW_CONFIDENCE = 0.40     # uniformly-low-confidence escalation cutoff

# Rationale score weights (sum to 1.0)
_W_GROUNDING = 0.35
_W_API = 0.25
_W_COMPLETENESS = 0.20
_W_SPECIFICITY = 0.20


@dataclass
class RepositoryFacts:
    """Deterministic facts extracted from the pair inputs."""

    identifiers: set[str] = field(default_factory=set)
    branch_a_identifiers: set[str] = field(default_factory=set)
    branch_b_identifiers: set[str] = field(default_factory=set)
    changed_api: set[str] = field(default_factory=set)


@dataclass
class RationaleScore:
    model_name: str
    verdict: str | None
    confidence: float
    total: float
    grounding: float
    api_alignment: float
    completeness: float
    specificity: float
    grounded_identifiers: list[str] = field(default_factory=list)
    hallucinated_identifiers: list[str] = field(default_factory=list)


@dataclass
class EvidenceAdjudication:
    final_verdict: FinalOutcome
    explanation: str = ""
    agreeing_models: list[str] = field(default_factory=list)
    dissenting_models: list[str] = field(default_factory=list)
    failed_models: list[str] = field(default_factory=list)
    weak_evidence_models: list[str] = field(default_factory=list)
    shared_evidence: list[str] = field(default_factory=list)
    evidence_overlap_score: float = 0.0
    decision_rule: str = ""
    rationale_scores: list[dict] = field(default_factory=list)
    model_summaries: list[dict] = field(default_factory=list)


def _diff_branch_identifiers(diff: str) -> set[str]:
    ids: set[str] = set()
    for line in diff.splitlines():
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
            ids.update(extract_identifiers(line[1:]))
    return ids


def _diff_api_symbols(diff: str) -> set[str]:
    symbols: set[str] = set()
    for pattern in (r"\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)", r"\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)"):
        for match in re.finditer(pattern, diff):
            symbols.add(match.group(1).lower())
    return symbols


def _structured_branch_facts(branch: dict[str, Any]) -> tuple[set[str], set[str]]:
    """Return (identifiers, api_symbols) for one branch of a structured delta."""
    identifiers: set[str] = set()
    api: set[str] = set()

    def add_function(fn: dict[str, Any] | None) -> None:
        if not fn:
            return
        name = fn.get("function_name")
        if name:
            short = name.split(".")[-1].lower()
            identifiers.add(short)
            api.add(short)
        for call in fn.get("calls") or ():
            identifiers.add(str(call).lower())
        for ident in fn.get("identifiers") or ():
            identifiers.add(str(ident).lower())

    for fn in branch.get("added", []) + branch.get("removed", []):
        add_function(fn)
    for change in branch.get("changed", []):
        add_function(change.get("merge_base"))
        add_function(change.get("branch"))
    for file_delta in branch.get("files", []):
        for key in (
            "identifiers_added",
            "identifiers_removed",
            "assignments_added",
            "assignments_removed",
        ):
            for ident in file_delta.get(key, []):
                identifiers.add(str(ident).lower())
        for key in ("assignments_added", "assignments_removed", "classes_added", "classes_removed"):
            for ident in file_delta.get(key, []):
                api.add(str(ident).split("(")[0].lower())
        for key in ("imports_added", "imports_removed"):
            for line in file_delta.get(key, []):
                identifiers.update(extract_identifiers(str(line)))
    return identifiers, api


def build_facts(
    branch_a_diff: str = "",
    branch_b_diff: str = "",
    structured_delta: dict[str, Any] | None = None,
) -> RepositoryFacts:
    facts = RepositoryFacts()
    facts.branch_a_identifiers = _diff_branch_identifiers(branch_a_diff)
    facts.branch_b_identifiers = _diff_branch_identifiers(branch_b_diff)
    facts.changed_api = _diff_api_symbols(branch_a_diff) | _diff_api_symbols(branch_b_diff)

    if structured_delta:
        ids_a, api_a = _structured_branch_facts(structured_delta.get("branch_a", {}))
        ids_b, api_b = _structured_branch_facts(structured_delta.get("branch_b", {}))
        facts.branch_a_identifiers |= ids_a
        facts.branch_b_identifiers |= ids_b
        facts.changed_api |= api_a | api_b
        for link in structured_delta.get("cross_branch_links", []):
            symbol = str(link.get("symbol", "")).lower()
            if symbol:
                facts.changed_api.add(symbol)
                facts.branch_a_identifiers.add(symbol)
                facts.branch_b_identifiers.add(symbol)

    facts.identifiers = facts.branch_a_identifiers | facts.branch_b_identifiers
    return facts


def _cited_identifiers(result: ModelResult) -> set[str]:
    if not result.verdict:
        return set()
    cited: set[str] = set()
    for item in result.verdict.evidence:
        cited.update(extract_identifiers(str(item)))
    cited.update(extract_identifiers(result.verdict.reasoning))
    return cited


def score_rationale(result: ModelResult, facts: RepositoryFacts) -> RationaleScore:
    """Deterministically score how well a rationale is grounded in the inputs."""
    verdict = result.verdict.verdict if result.verdict else None
    confidence = result.verdict.confidence if result.verdict else 0.0
    cited = _cited_identifiers(result)

    grounded = sorted(cited & facts.identifiers)
    hallucinated = sorted(cited - facts.identifiers) if facts.identifiers else []

    grounding = len(grounded) / len(cited) if cited else 0.0
    api_hits = cited & facts.changed_api
    api_norm = min(len(facts.changed_api), 3) or 1
    api_alignment = min(1.0, len(api_hits) / api_norm) if facts.changed_api else grounding

    covers_a = bool(cited & facts.branch_a_identifiers) or not facts.branch_a_identifiers
    covers_b = bool(cited & facts.branch_b_identifiers) or not facts.branch_b_identifiers
    completeness = 0.5 * covers_a + 0.5 * covers_b

    specificity = min(1.0, len(grounded) / 4)

    total = (
        _W_GROUNDING * grounding
        + _W_API * api_alignment
        + _W_COMPLETENESS * completeness
        + _W_SPECIFICITY * specificity
    )
    return RationaleScore(
        model_name=result.model_name,
        verdict=verdict,
        confidence=confidence,
        total=round(total, 4),
        grounding=round(grounding, 4),
        api_alignment=round(api_alignment, 4),
        completeness=round(completeness, 4),
        specificity=round(specificity, 4),
        grounded_identifiers=grounded,
        hallucinated_identifiers=hallucinated,
    )


def _score_dict(score: RationaleScore) -> dict:
    return {
        "model": score.model_name,
        "verdict": score.verdict,
        "confidence": score.confidence,
        "total": score.total,
        "grounding": score.grounding,
        "api_alignment": score.api_alignment,
        "completeness": score.completeness,
        "specificity": score.specificity,
        "grounded_identifiers": score.grounded_identifiers,
        "hallucinated_identifiers": score.hallucinated_identifiers,
    }


def adjudicate_v2(
    results: list[ModelResult],
    *,
    branch_a_diff: str = "",
    branch_b_diff: str = "",
    structured_delta: dict[str, Any] | None = None,
) -> EvidenceAdjudication:
    facts = build_facts(branch_a_diff, branch_b_diff, structured_delta)
    ok_results = [r for r in results if r.outcome == "ok" and r.verdict is not None]
    failed = [r.model_name for r in results if r.outcome != "ok"]

    scores = [score_rationale(r, facts) for r in ok_results]
    score_dicts = [_score_dict(s) for s in scores]
    weak = [s.model_name for s in scores if not s.grounded_identifiers]

    if not ok_results:
        return EvidenceAdjudication(
            final_verdict="escalate",
            explanation="All models failed; nothing to adjudicate.",
            failed_models=failed,
            decision_rule="all_failed",
            rationale_scores=score_dicts,
        )

    by_verdict: dict[str, list[RationaleScore]] = {"conflict": [], "no_conflict": []}
    for s in scores:
        if s.verdict in by_verdict:
            by_verdict[s.verdict].append(s)

    shared = sorted(
        set.intersection(*(set(s.grounded_identifiers) for s in scores))
        if scores
        else set()
    )

    # Unanimous verdict resolves directly; evidence quality is recorded, not
    # used as an extra reason to escalate.
    present = [v for v, group in by_verdict.items() if group]
    if len(present) == 1:
        verdict = present[0]
        return EvidenceAdjudication(
            final_verdict=verdict,
            explanation=(
                f"All {len(ok_results)} models agree on '{verdict}' "
                f"(best rationale score "
                f"{max(s.total for s in scores):.2f})."
            ),
            agreeing_models=[s.model_name for s in scores],
            failed_models=failed,
            weak_evidence_models=weak,
            shared_evidence=shared,
            evidence_overlap_score=max(s.total for s in scores),
            decision_rule="unanimous",
            rationale_scores=score_dicts,
        )

    best_conflict = max(by_verdict["conflict"], key=lambda s: s.total)
    best_no_conflict = max(by_verdict["no_conflict"], key=lambda s: s.total)
    dominant, other = (
        (best_conflict, best_no_conflict)
        if best_conflict.total >= best_no_conflict.total
        else (best_no_conflict, best_conflict)
    )
    margin = dominant.total - other.total

    def result_for(verdict: str, rule: str, explanation: str) -> EvidenceAdjudication:
        agreeing = [s.model_name for s in scores if s.verdict == verdict]
        dissenting = [s.model_name for s in scores if s.verdict != verdict]
        return EvidenceAdjudication(
            final_verdict=verdict,
            explanation=explanation,
            agreeing_models=agreeing,
            dissenting_models=dissenting,
            failed_models=failed,
            weak_evidence_models=weak,
            shared_evidence=shared,
            evidence_overlap_score=margin,
            decision_rule=rule,
            rationale_scores=score_dicts,
        )

    # Step 3: a clearly dominant rationale wins, even against a majority.
    if margin >= DOMINANCE_MARGIN:
        assert dominant.verdict is not None
        return result_for(
            dominant.verdict,
            "rationale_dominance",
            (
                f"{dominant.model_name} gave the strongest grounded rationale "
                f"(score {dominant.total:.2f} vs {other.total:.2f}, margin "
                f"{margin:.2f} >= {DOMINANCE_MARGIN}); verdict '{dominant.verdict}' "
                f"accepted over {other.model_name} despite the vote split. "
                f"Grounded evidence: {dominant.grounded_identifiers or 'none'}."
            ),
        )

    # Escalate on uniformly low confidence.
    if all(s.confidence < LOW_CONFIDENCE for s in scores):
        return EvidenceAdjudication(
            final_verdict="escalate",
            explanation=(
                "Verdicts disagree and every model reported confidence below "
                f"{LOW_CONFIDENCE}; escalating."
            ),
            agreeing_models=[s.model_name for s in scores],
            failed_models=failed,
            weak_evidence_models=weak,
            shared_evidence=shared,
            evidence_overlap_score=margin,
            decision_rule="uniform_low_confidence",
            rationale_scores=score_dicts,
        )

    # Tie-breaker: best confidence-weighted rationale per side (not a sum —
    # summing would just reintroduce majority voting).
    weight_conflict = max(s.total * s.confidence for s in by_verdict["conflict"])
    weight_no_conflict = max(s.total * s.confidence for s in by_verdict["no_conflict"])
    gap = abs(weight_conflict - weight_no_conflict)
    if gap >= WEIGHT_EPSILON:
        verdict = "conflict" if weight_conflict > weight_no_conflict else "no_conflict"
        return result_for(
            verdict,
            "weighted_evidence_vote",
            (
                f"Rationale quality is comparable (margin {margin:.2f} < "
                f"{DOMINANCE_MARGIN}); confidence-weighted evidence favors "
                f"'{verdict}' (conflict={weight_conflict:.2f} vs "
                f"no_conflict={weight_no_conflict:.2f}, gap {gap:.2f})."
            ),
        )

    return EvidenceAdjudication(
        final_verdict="escalate",
        explanation=(
            f"Contradictory verdicts with rationale scores within {DOMINANCE_MARGIN} "
            f"(margin {margin:.2f}) and weighted evidence within {WEIGHT_EPSILON} "
            f"(gap {gap:.2f}); genuine ambiguity, escalating."
        ),
        agreeing_models=[s.model_name for s in scores],
        failed_models=failed,
        weak_evidence_models=weak,
        shared_evidence=shared,
        evidence_overlap_score=margin,
        decision_rule="ambiguous_evidence",
        rationale_scores=score_dicts,
    )
