"""Evidence-weighted adjudication: score rationales, don't just count votes.

FROZEN — Adjudicator v3 (behavior-break gate). Do not change this module until
after a full re-eval, evaluation write-up, and independent audit. See
results/adjudicator_v3_verification.md and results/adjudicator_v3_freeze.json.
"""

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
    semantic_changed_symbols: set[str] = field(default_factory=set)
    cross_branch_risk_symbols: set[str] = field(default_factory=set)


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
    break_evidence: float = 0.0
    causal_chain: float = 0.0
    speculation_penalty: float = 0.0
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


def _is_executable_removal(line: str) -> bool:
    """Whether a removed diff line represents behavior, not docs/whitespace."""
    if not line.startswith("-") or line.startswith("---"):
        return False
    text = line[1:].strip()
    if not text or text.startswith("#"):
        return False
    if text.startswith(('"""', "'''")):
        return False
    return True


def _semantic_changed_symbols(diff: str) -> set[str]:
    """Functions whose hunks remove executable code or a prior signature."""
    changed: set[str] = set()
    current_function: str | None = None
    for line in diff.splitlines():
        match = re.search(r"\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)", line)
        if match:
            current_function = match.group(1).lower()
        if _is_executable_removal(line) and current_function:
            changed.add(current_function)
    return changed


def _added_identifiers(diff: str) -> set[str]:
    identifiers: set[str] = set()
    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            identifiers.update(extract_identifiers(line[1:]))
    return identifiers


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
    changed_a = _semantic_changed_symbols(branch_a_diff)
    changed_b = _semantic_changed_symbols(branch_b_diff)
    facts.semantic_changed_symbols = changed_a | changed_b
    facts.cross_branch_risk_symbols = (
        (changed_a & _added_identifiers(branch_b_diff))
        | (changed_b & _added_identifiers(branch_a_diff))
    )

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
                facts.cross_branch_risk_symbols.add(symbol)

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


_SPECULATION_PATTERNS = (
    r"\bmight\b",
    r"\bmay\b",
    r"\bcould\b",
    r"\blikely\b",
    r"\bseems?\b",
    r"\bpossibly\b",
    r"\bunclear\b",
    r"\bpotential(?:ly)?\b",
    r"\bprobably\b",
)

_BREAK_PATTERNS = (
    r"\b(?:name|import|type|attribute)error\b",
    r"\bstale\s+(?:call|caller|import|reference)\b",
    r"\bno longer (?:exists|accepts|returns|raises)\b",
    r"\b(?:remove|removed|rename|renamed)\w*\b.{0,80}\b(?:call|caller|import|reference)\b",
    r"\b(?:signature|argument|parameter).{0,60}\b(?:mismatch|break|invalid)\b",
    r"\b(?:exception|error).{0,60}\b(?:mismatch|uncaught|not caught|swallowed)\b",
    r"\b(?:mutates?|modifies?)\b.{0,60}\b(?:original|caller|input|owned)\b",
    r"\b(?:alias|ownership|copy)\b.{0,60}\b(?:mutation|mutates|corrupt)\b",
    r"\b(?:default|boundary|sentinel|ordering|case.sensitiv).{0,80}\b"
    r"(?:changes?|violat|incorrect|wrong|break|fail)\b",
)

_CAUSAL_PATTERNS = (
    r"\bbecause\b",
    r"\btherefore\b",
    r"\bcauses?\b",
    r"\bleads? to\b",
    r"\bresults? in\b",
    r"\bbreaks?\b",
    r"\bafter (?:the )?merge\b",
    r"\bwhile branch\b",
    r"->|→",
)


def _rationale_text(result: ModelResult) -> str:
    if not result.verdict:
        return ""
    return " ".join(
        [result.verdict.reasoning, *[str(item) for item in result.verdict.evidence]]
    ).lower()


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
    text = _rationale_text(result)
    speculation_hits = sum(bool(re.search(pattern, text)) for pattern in _SPECULATION_PATTERNS)
    speculation_penalty = min(0.5, speculation_hits * 0.12)
    causal_chain = 1.0 if any(re.search(pattern, text) for pattern in _CAUSAL_PATTERNS) else 0.0

    risk_hits = set(grounded) & facts.cross_branch_risk_symbols
    mechanism = any(re.search(pattern, text) for pattern in _BREAK_PATTERNS)
    break_evidence = 0.0
    if verdict == "conflict" and risk_hits:
        break_evidence = 0.5
        if mechanism:
            break_evidence += 0.3
        if causal_chain:
            break_evidence += 0.2
    break_evidence = min(1.0, break_evidence)

    total = (
        _W_GROUNDING * grounding
        + _W_API * api_alignment
        + _W_COMPLETENESS * completeness
        + _W_SPECIFICITY * specificity
    )
    if verdict == "conflict":
        # Identifier-rich conflict prose is not enough: it must connect a
        # real cross-branch behavior change to a concrete failure mechanism.
        total *= 0.45 + 0.55 * break_evidence
    total = max(0.0, total - speculation_penalty)
    return RationaleScore(
        model_name=result.model_name,
        verdict=verdict,
        confidence=confidence,
        total=round(total, 4),
        grounding=round(grounding, 4),
        api_alignment=round(api_alignment, 4),
        completeness=round(completeness, 4),
        specificity=round(specificity, 4),
        break_evidence=round(break_evidence, 4),
        causal_chain=round(causal_chain, 4),
        speculation_penalty=round(speculation_penalty, 4),
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
        "break_evidence": score.break_evidence,
        "causal_chain": score.causal_chain,
        "speculation_penalty": score.speculation_penalty,
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

    # Preserve abstention when every model is uncertain; the behavior-break
    # burden of proof should not convert uniformly weak evidence into SAFE.
    if len([v for v, group in by_verdict.items() if group]) > 1 and all(
        s.confidence < LOW_CONFIDENCE for s in scores
    ):
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
            evidence_overlap_score=0.0,
            decision_rule="uniform_low_confidence",
            rationale_scores=score_dicts,
        )

    # Burden of proof: a conflict verdict is admissible only when a rationale
    # identifies a real symbol changed on one branch and used on the other,
    # then gives a causal explanation of the resulting behavior break.
    admissible_conflicts = [
        s
        for s in by_verdict["conflict"]
        if s.break_evidence >= 0.7
        and s.causal_chain > 0
        and bool(s.grounded_identifiers)
    ]
    if by_verdict["conflict"] and not admissible_conflicts:
        no_conflict_scores = by_verdict["no_conflict"]
        return EvidenceAdjudication(
            final_verdict="no_conflict",
            explanation=(
                "Conflict rejected: no rationale demonstrated a grounded "
                "cross-branch behavior break with a causal chain. "
                f"Static risk symbols: {sorted(facts.cross_branch_risk_symbols)}."
            ),
            agreeing_models=[s.model_name for s in no_conflict_scores],
            dissenting_models=[s.model_name for s in by_verdict["conflict"]],
            failed_models=failed,
            weak_evidence_models=weak,
            shared_evidence=shared,
            evidence_overlap_score=max(
                (s.break_evidence for s in by_verdict["conflict"]), default=0.0
            ),
            decision_rule="conflict_evidence_gate",
            rationale_scores=score_dicts,
        )

    if admissible_conflicts:
        strongest = max(
            admissible_conflicts,
            key=lambda score: (score.break_evidence, score.total),
        )
        return EvidenceAdjudication(
            final_verdict="conflict",
            explanation=(
                f"{strongest.model_name} demonstrated a grounded cross-branch "
                "behavior break with a causal chain. "
                f"Risk symbols: {sorted(facts.cross_branch_risk_symbols)}; "
                f"break evidence={strongest.break_evidence:.2f}."
            ),
            agreeing_models=[s.model_name for s in admissible_conflicts],
            dissenting_models=[
                s.model_name for s in scores if s.verdict != "conflict"
            ],
            failed_models=failed,
            weak_evidence_models=weak,
            shared_evidence=shared,
            evidence_overlap_score=strongest.break_evidence,
            decision_rule="grounded_behavior_break",
            rationale_scores=score_dicts,
        )

    # Unsupported conflict rationales cannot win a disagreement by length,
    # confidence, or identifier count.
    by_verdict["conflict"] = admissible_conflicts

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
