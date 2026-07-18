"""Evidence-aware adjudication across committee model verdicts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Literal

from quorum.models import ModelResult, VerdictLabel

FinalOutcome = Literal["compatible", "conflict", "escalate"]

# English + generic review vocabulary — excluded from identifier overlap.
_STOPWORDS = frozenset(
    {
        "the", "and", "for", "that", "this", "with", "from", "into", "when",
        "will", "would", "could", "should", "have", "has", "had", "been",
        "are", "was", "were", "not", "but", "can", "may", "also", "both",
        "branch", "branches", "merge", "merged", "merging", "change", "changes",
        "changed", "adding", "added", "removes", "removed", "uses", "using",
        "function", "functions", "method", "methods", "name", "names", "file",
        "files", "line", "lines", "diff", "diffs", "code", "result", "logic",
        "logical", "semantically", "semantic", "conflict", "conflicts",
        "compatible", "incompatible", "because", "since", "while", "after",
        "before", "same", "different", "new", "old", "type", "types", "call",
        "calls", "called", "calling", "import", "imports", "imported",
        "module", "modules", "class", "classes", "test", "tests", "case",
        "cases", "true", "false", "none", "null", "via", "etc", "e.g", "ie",
        "one", "two", "three", "first", "second", "other", "each", "all",
        "any", "some", "such", "than", "then", "there", "their", "they",
        "them", "these", "those", "which", "what", "where", "how", "why",
        "who", "being", "does", "did", "just", "only", "very", "much", "more",
        "most", "less", "over", "under", "between", "within", "without",
        "about", "against", "during", "through", "upon", "out", "off", "up",
        "down", "left", "right", "still", "even", "well", "back", "here",
        "introduce", "introduces", "introduced", "lead", "leads", "leading",
        "break", "breaks", "broken", "cause", "causes", "causing", "make",
        "makes", "made", "exist", "exists", "existing", "present", "absent",
        "overlap", "overlaps", "overlapping", "textual", "correct", "incorrect",
        "valid", "invalid", "expected", "unexpected", "behavior", "behaviour",
        "implementation", "implementations", "definition", "definitions",
        "validation", "validate", "pattern", "patterns", "regex", "string",
        "strings", "data", "input", "inputs", "output", "outputs", "api",
        "apis", "contract", "contracts", "feature", "features", "orthogonal",
        "distinct", "separate", "independently", "together", "combined",
        "combination", "manner", "terms", "term", "way", "ways", "part",
        "parts", "portion", "portions", "section", "sections", "area", "areas",
        "location", "locations", "point", "points", "issue", "issues", "problem",
        "problems", "error", "errors", "fail", "fails", "failure", "failures",
        "reason", "reasons", "reasoning", "evidence", "detail", "details",
        "content", "contents", "description", "descriptions", "summary",
        "analysis", "note", "notes", "example", "examples", "specific",
        "general", "overall", "entire", "entirely", "fully", "partially",
        "likely", "unlikely", "possible", "impossible", "perhaps", "maybe",
        "rename", "renames", "renamed", "renaming", "stale", "reference",
        "references", "referenced", "referencing", "caller", "callers",
        "cited", "cite", "cites", "citing", "shared", "common", "similar",
        "related", "unrelated", "coincidental", "coincidentally", "agree",
        "agrees", "agreed", "agreement", "disagree", "disagrees", "disagreement",
        "majority", "minority", "model", "models", "verdict", "confidence",
        "utils", "checkout", "init", "main", "self", "return", "pass", "def",
    }
)

_IDENTIFIER_MIN_LEN = 3
_OVERLAP_THRESHOLD = 0.25


@dataclass
class AdjudicationResult:
    final_verdict: FinalOutcome
    agreeing_models: list[str] = field(default_factory=list)
    dissenting_models: list[str] = field(default_factory=list)
    failed_models: list[str] = field(default_factory=list)
    weak_evidence_models: list[str] = field(default_factory=list)
    evidence_overlap_score: float = 0.0
    shared_evidence: list[str] = field(default_factory=list)
    explanation: str = ""
    model_summaries: list[dict] = field(default_factory=list)


def adjudicate(
    results: list[ModelResult],
    *,
    branch_a_diff: str = "",
    branch_b_diff: str = "",
    structured_delta: dict[str, Any] | None = None,
) -> AdjudicationResult:
    ok_results = [r for r in results if r.outcome == "ok" and r.verdict is not None]
    failed = [r.model_name for r in results if r.outcome != "ok"]
    diff_ids = _diff_identifiers(branch_a_diff, branch_b_diff, structured_delta)

    if not ok_results:
        return AdjudicationResult(
            final_verdict="escalate",
            failed_models=failed,
            explanation="All models failed; cannot adjudicate.",
            model_summaries=_summarize_all(results, diff_ids),
        )

    if len(ok_results) == 1:
        only = ok_results[0]
        assert only.verdict is not None
        ids = _model_identifiers(only)
        return AdjudicationResult(
            final_verdict=only.verdict.verdict,
            agreeing_models=[only.model_name],
            failed_models=failed,
            weak_evidence_models=[only.model_name] if not ids else [],
            evidence_overlap_score=1.0,
            shared_evidence=sorted(ids) if ids else only.verdict.evidence,
            explanation=(
                f"Single successful model ({only.model_name}) returned "
                f"'{only.verdict.verdict}'."
            ),
            model_summaries=_summarize_all(results, diff_ids),
        )

    by_verdict: dict[VerdictLabel, list[ModelResult]] = {"compatible": [], "conflict": []}
    for result in ok_results:
        assert result.verdict is not None
        by_verdict[result.verdict.verdict].append(result)

    majority_label: VerdictLabel | None = None
    majority_group: list[ModelResult] = []
    minority_group: list[ModelResult] = []

    if len(by_verdict["conflict"]) > len(by_verdict["compatible"]):
        majority_label = "conflict"
        majority_group = by_verdict["conflict"]
        minority_group = by_verdict["compatible"]
    elif len(by_verdict["compatible"]) > len(by_verdict["conflict"]):
        majority_label = "compatible"
        majority_group = by_verdict["compatible"]
        minority_group = by_verdict["conflict"]
    else:
        return AdjudicationResult(
            final_verdict="escalate",
            agreeing_models=[r.model_name for r in ok_results],
            failed_models=failed,
            explanation=(
                "Models split evenly between 'compatible' and 'conflict'; "
                "escalating rather than forcing a majority vote."
            ),
            model_summaries=_summarize_all(results, diff_ids),
        )

    overlap_score, shared_ids, weak_models = _identifier_overlap(majority_group, diff_ids)

    if minority_group:
        minority_names = [r.model_name for r in minority_group]
        minority_verdicts = {r.model_name: r.verdict.verdict for r in minority_group if r.verdict}
        return AdjudicationResult(
            final_verdict="escalate",
            agreeing_models=[r.model_name for r in majority_group],
            dissenting_models=minority_names,
            failed_models=failed,
            weak_evidence_models=weak_models,
            evidence_overlap_score=overlap_score,
            shared_evidence=shared_ids,
            explanation=(
                f"Disagreement: majority ({len(majority_group)} models) say '{majority_label}' "
                f"but {', '.join(minority_names)} disagree "
                f"({', '.join(f'{n}={minority_verdicts[n]}' for n in minority_names)}). "
                f"Shared identifiers among agreeing models: {shared_ids or 'none'} "
                f"(overlap={overlap_score:.2f})."
            ),
            model_summaries=_summarize_all(results, diff_ids),
        )

    if overlap_score < _OVERLAP_THRESHOLD and len(majority_group) > 1:
        return AdjudicationResult(
            final_verdict="escalate",
            agreeing_models=[r.model_name for r in majority_group],
            failed_models=failed,
            weak_evidence_models=weak_models,
            evidence_overlap_score=overlap_score,
            shared_evidence=shared_ids,
            explanation=(
                f"All {len(majority_group)} models agree on '{majority_label}', but cited "
                f"evidence shares too few code identifiers (overlap={overlap_score:.2f}, "
                f"shared={shared_ids or 'none'}). "
                "Agreement may be coincidental; escalating."
            ),
            model_summaries=_summarize_all(results, diff_ids),
        )

    assert majority_label is not None
    return AdjudicationResult(
        final_verdict=majority_label,
        agreeing_models=[r.model_name for r in majority_group],
        failed_models=failed,
        weak_evidence_models=weak_models,
        evidence_overlap_score=overlap_score,
        shared_evidence=shared_ids,
        explanation=(
            f"{len(majority_group)} models agree on '{majority_label}' with "
            f"identifier overlap score {overlap_score:.2f}."
            + (f" Shared identifiers: {shared_ids}" if shared_ids else "")
            + (f" Weak evidence (excluded from overlap): {', '.join(weak_models)}" if weak_models else "")
        ),
        model_summaries=_summarize_all(results, diff_ids),
    )


def _clean_identifier(token: str) -> str | None:
    token = token.strip().strip("`'\"")
    if not token:
        return None
    # Take last segment of dotted paths (utils.calculate_total -> calculate_total)
    if "." in token and not token.endswith((".py", ".go", ".ts", ".tsx", ".rs", ".js")):
        token = token.split(".")[-1]
    token = token.lower()
    if len(token) < _IDENTIFIER_MIN_LEN:
        return None
    if token in _STOPWORDS:
        return None
    if token.isdigit():
        return None
    if not re.match(r"^[a-z_][a-z0-9_]*$", token):
        return None
    return token


def extract_identifiers(text: str) -> set[str]:
    """Pull code-like identifier tokens from evidence/reasoning prose."""
    if not text:
        return set()

    found: set[str] = set()

    # Backticks, quotes, JSON-ish keys
    for pattern in (
        r"`([^`]+)`",
        r'"([a-zA-Z_][a-zA-Z0-9_]*)"',
        r"'([a-zA-Z_][a-zA-Z0-9_]*)'",
    ):
        for match in re.finditer(pattern, text):
            cleaned = _clean_identifier(match.group(1))
            if cleaned:
                found.add(cleaned)

    # File paths: foo.py, bar.go
    for match in re.finditer(r"\b([a-zA-Z_][\w.-]*\.(?:py|go|ts|tsx|rs|js))\b", text):
        cleaned = _clean_identifier(match.group(1).replace(".", "_").replace("-", "_"))
        if cleaned:
            found.add(cleaned)

    # Function-call syntax: name(
    for match in re.finditer(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", text):
        cleaned = _clean_identifier(match.group(1))
        if cleaned:
            found.add(cleaned)

    # snake_case identifiers; split camelCase only when no underscore present
    for match in re.finditer(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", text):
        raw = match.group(1)
        cleaned = _clean_identifier(raw)
        if cleaned:
            found.add(cleaned)
            if "_" in raw:
                continue
        if "_" not in raw:
            for part in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|[0-9]+", raw):
                part_clean = _clean_identifier(part)
                if part_clean and len(part_clean) >= 4:
                    found.add(part_clean)

    return _drop_identifier_fragments(found)


def _drop_identifier_fragments(ids: set[str]) -> set[str]:
    """Remove tokens that are strict substrings of another identifier in the set."""
    if len(ids) <= 1:
        return ids
    keep: set[str] = set()
    sorted_ids = sorted(ids, key=len, reverse=True)
    for ident in sorted_ids:
        if any(ident != other and ident in other for other in keep):
            continue
        keep.add(ident)
    return keep


def _model_identifiers(result: ModelResult) -> set[str]:
    if not result.verdict:
        return set()
    ids: set[str] = set()
    for item in result.verdict.evidence:
        if isinstance(item, dict):
            ids.update(extract_identifiers(json.dumps(item)))
        else:
            ids.update(extract_identifiers(str(item)))
    ids.update(extract_identifiers(result.verdict.reasoning))
    return ids


def _diff_identifiers(
    branch_a_diff: str,
    branch_b_diff: str,
    structured_delta: dict[str, Any] | None,
) -> set[str]:
    ids: set[str] = set()
    for diff in (branch_a_diff, branch_b_diff):
        for line in diff.splitlines():
            if line.startswith(("+", "-")):
                ids.update(extract_identifiers(line[1:]))
        # def name, class name in diff context
        for match in re.finditer(r"\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)", diff):
            cleaned = _clean_identifier(match.group(1))
            if cleaned:
                ids.add(cleaned)
        for match in re.finditer(r"\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)", diff):
            cleaned = _clean_identifier(match.group(1))
            if cleaned:
                ids.add(cleaned)

    if structured_delta:
        for branch_key in ("branch_a", "branch_b"):
            branch = structured_delta.get(branch_key, {})
            for fn in branch.get("added", []) + branch.get("removed", []):
                name = fn.get("function_name")
                if name:
                    cleaned = _clean_identifier(name)
                    if cleaned:
                        ids.add(cleaned)
            for change in branch.get("changed", []):
                for side in ("merge_base", "branch"):
                    fn = change.get(side) or {}
                    name = fn.get("function_name")
                    if name:
                        cleaned = _clean_identifier(name)
                        if cleaned:
                            ids.add(cleaned)
                for call in change.get("calls", []):
                    cleaned = _clean_identifier(str(call))
                    if cleaned:
                        ids.add(cleaned)
        for link in structured_delta.get("cross_branch_links", []):
            sym = link.get("symbol")
            if sym:
                cleaned = _clean_identifier(str(sym))
                if cleaned:
                    ids.add(cleaned)

    return ids


def _is_weak_evidence(ids: set[str], diff_ids: set[str]) -> bool:
    """Vague citations like 'Branch A diff' with no code identifiers."""
    if not ids:
        return True
    if diff_ids:
        return not (ids & diff_ids)
    # Without diff context, require at least one identifier that looks like a symbol
    return len(ids) < 1


def _identifier_overlap(
    group: list[ModelResult],
    diff_ids: set[str],
) -> tuple[float, list[str], list[str]]:
    if len(group) <= 1:
        ids = sorted(_model_identifiers(group[0])) if group else []
        return 1.0, ids, []

    per_model: dict[str, set[str]] = {
        r.model_name: _model_identifiers(r) for r in group
    }
    weak_models = [
        name for name, ids in per_model.items() if _is_weak_evidence(ids, diff_ids)
    ]
    contributing = {
        name: ids for name, ids in per_model.items() if name not in weak_models
    }

    if len(contributing) < 2:
        # Unanimous verdict with at most one strong citation — use diff-grounded ids
        all_ids = set.union(*per_model.values()) if per_model else set()
        grounded = sorted(all_ids & diff_ids) if diff_ids else sorted(all_ids)
        if len(contributing) == 1 and grounded:
            return 1.0, grounded, weak_models
        if len(contributing) == 0 and len(weak_models) == len(group):
            return 0.0, [], weak_models
        single = next(iter(contributing.values()), set())
        return (1.0 if single else 0.0), sorted(single), weak_models

    id_sets = list(contributing.values())
    intersection = set.intersection(*id_sets)
    union = set.union(*id_sets)

    # Prefer identifiers that appear in the actual diff/input
    if diff_ids:
        intersection = {i for i in intersection if i in diff_ids} or intersection
        union = {i for i in union if i in diff_ids} or union

    score = len(intersection) / len(union) if union else 0.0
    return score, sorted(intersection), weak_models


def _summarize_all(results: list[ModelResult], diff_ids: set[str]) -> list[dict]:
    summaries = []
    for result in results:
        ids = _model_identifiers(result)
        entry = {
            "model": result.model_name,
            "role": result.role,
            "outcome": result.outcome,
            "elapsed_seconds": round(result.elapsed_seconds, 2),
            "evidence_identifiers": sorted(ids),
            "evidence_quality": (
                "weak" if _is_weak_evidence(ids, diff_ids) else "strong"
            ),
        }
        if result.verdict:
            entry.update(
                {
                    "verdict": result.verdict.verdict,
                    "confidence": result.verdict.confidence,
                    "reasoning": result.verdict.reasoning,
                    "evidence": result.verdict.evidence,
                }
            )
        if result.error:
            entry["error"] = result.error
        summaries.append(entry)
    return summaries
