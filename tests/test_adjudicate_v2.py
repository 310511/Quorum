"""Tests for evidence-weighted adjudication."""

from __future__ import annotations

from quorum.adjudicate_v2 import (
    adjudicate_v2,
    build_facts,
    score_rationale,
)
from quorum.models import ModelResult, VerdictResponse

BRANCH_A_DIFF = """\
--- a/utils.py
+++ b/utils.py
@@ -1,4 +1,4 @@
-def calculate_total(items):
+def compute_grand_total(items):
     return sum(item.price for item in items)
"""

BRANCH_B_DIFF = """\
--- a/report.py
+++ b/report.py
@@ -1,3 +1,4 @@
 def build_report(items):
+    total = calculate_total(items)
     return render(items)
"""

SAFE_BRANCH_A_DIFF = """\
--- a/utils.py
+++ b/utils.py
@@ -1,2 +1,3 @@
 def calculate_total(items):
+    \"\"\"Calculate the total without changing behavior.\"\"\"
     return sum(item.price for item in items)
"""

SAFE_BRANCH_B_DIFF = """\
--- a/report.py
+++ b/report.py
@@ -0,0 +1,2 @@
+def build_report(items):
+    return calculate_total(items)
"""


def _result(
    name: str,
    verdict: str,
    confidence: float,
    reasoning: str,
    evidence: list[str] | None = None,
) -> ModelResult:
    return ModelResult(
        model_name=name,
        role="committee",
        outcome="ok",
        verdict=VerdictResponse(
            verdict=verdict,  # type: ignore[arg-type]
            original_verdict=verdict,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence or [],
        ),
    )


def test_strong_grounded_rationale_beats_two_weak_votes() -> None:
    """A 2-vs-1 vote must not escalate when the minority rationale dominates."""
    results = [
        _result(
            "deepseek",
            "conflict",
            0.9,
            "Branch A renames `calculate_total` to `compute_grand_total` while "
            "branch B adds a new call to `calculate_total` in `build_report`; "
            "the merged code raises NameError.",
            ["calculate_total", "compute_grand_total", "build_report"],
        ),
        _result("gemma", "no_conflict", 0.6, "The changes look fine to me overall."),
        _result(
            "llama",
            "no_conflict",
            0.5,
            "Branch B modifies the frobnicate_widget subsystem which is unrelated.",
            ["frobnicate_widget"],
        ),
    ]
    outcome = adjudicate_v2(
        results, branch_a_diff=BRANCH_A_DIFF, branch_b_diff=BRANCH_B_DIFF
    )
    assert outcome.final_verdict == "conflict"
    assert outcome.decision_rule == "grounded_behavior_break"
    assert "deepseek" in outcome.agreeing_models


def test_unanimous_verdict_resolves_without_escalation() -> None:
    results = [
        _result("a", "no_conflict", 0.8, "Changes touch unrelated files."),
        _result("b", "no_conflict", 0.7, "No shared symbols between branches."),
        _result("c", "no_conflict", 0.9, "Independent changes."),
    ]
    outcome = adjudicate_v2(
        results, branch_a_diff=BRANCH_A_DIFF, branch_b_diff=BRANCH_B_DIFF
    )
    assert outcome.final_verdict == "no_conflict"
    assert outcome.decision_rule == "unanimous"


def test_uniformly_low_confidence_escalates() -> None:
    results = [
        _result("a", "conflict", 0.2, "Maybe there is a problem somewhere."),
        _result("b", "no_conflict", 0.3, "Probably fine but hard to tell."),
        _result("c", "no_conflict", 0.1, "Unsure."),
    ]
    outcome = adjudicate_v2(
        results, branch_a_diff=BRANCH_A_DIFF, branch_b_diff=BRANCH_B_DIFF
    )
    assert outcome.final_verdict == "escalate"
    assert outcome.decision_rule == "uniform_low_confidence"


def test_comparable_rationales_fall_back_to_weighted_vote() -> None:
    """Disagreement with similar-quality grounded rationales should still decide."""
    results = [
        _result(
            "a",
            "conflict",
            0.9,
            "Rename of `calculate_total` breaks the new call in `build_report`.",
            ["calculate_total", "build_report", "compute_grand_total"],
        ),
        _result(
            "b",
            "no_conflict",
            0.4,
            "`build_report` and `calculate_total` are in different files.",
            ["build_report", "calculate_total", "compute_grand_total"],
        ),
    ]
    outcome = adjudicate_v2(
        results, branch_a_diff=BRANCH_A_DIFF, branch_b_diff=BRANCH_B_DIFF
    )
    assert outcome.final_verdict == "conflict"
    assert outcome.decision_rule == "grounded_behavior_break"


def test_all_failed_escalates() -> None:
    failed = ModelResult(model_name="x", role="committee", outcome="error", error="boom")
    outcome = adjudicate_v2([failed], branch_a_diff=BRANCH_A_DIFF)
    assert outcome.final_verdict == "escalate"
    assert outcome.decision_rule == "all_failed"


def test_hallucinated_rationale_scores_lower_than_grounded() -> None:
    facts = build_facts(branch_a_diff=BRANCH_A_DIFF, branch_b_diff=BRANCH_B_DIFF)
    grounded = score_rationale(
        _result(
            "good",
            "conflict",
            0.9,
            "`calculate_total` renamed to `compute_grand_total`; `build_report` breaks.",
            ["calculate_total", "compute_grand_total", "build_report"],
        ),
        facts,
    )
    hallucinated = score_rationale(
        _result(
            "bad",
            "no_conflict",
            0.9,
            "The `frobnicate_widget` and `quantum_flux` helpers are unaffected.",
            ["frobnicate_widget", "quantum_flux"],
        ),
        facts,
    )
    assert grounded.total > hallucinated.total
    assert hallucinated.hallucinated_identifiers
    assert grounded.grounded_identifiers


def test_conflict_requires_grounded_cross_branch_behavior_break() -> None:
    """A confident majority cannot call a docstring-only twin a conflict."""
    results = [
        _result(
            "a",
            "conflict",
            0.95,
            "`calculate_total` and `build_report` might be semantically incompatible.",
            ["calculate_total", "build_report"],
        ),
        _result(
            "b",
            "conflict",
            0.9,
            "The new report helper could conflict with the existing total helper.",
            ["calculate_total", "build_report"],
        ),
        _result(
            "c",
            "no_conflict",
            0.9,
            "Branch A only adds documentation; `build_report` calls the unchanged "
            "`calculate_total` behavior.",
            ["calculate_total", "build_report"],
        ),
    ]
    outcome = adjudicate_v2(
        results,
        branch_a_diff=SAFE_BRANCH_A_DIFF,
        branch_b_diff=SAFE_BRANCH_B_DIFF,
    )
    assert outcome.final_verdict == "no_conflict"
    assert outcome.decision_rule == "conflict_evidence_gate"


def test_causal_break_evidence_is_recorded() -> None:
    facts = build_facts(branch_a_diff=BRANCH_A_DIFF, branch_b_diff=BRANCH_B_DIFF)
    score = score_rationale(
        _result(
            "grounded",
            "conflict",
            0.9,
            "Branch A renames `calculate_total` while branch B still calls "
            "`calculate_total`; therefore `build_report` raises NameError after merge.",
            ["calculate_total", "compute_grand_total", "build_report"],
        ),
        facts,
    )
    assert score.break_evidence >= 0.7
    assert score.causal_chain == 1.0


def test_speculation_penalizes_otherwise_similar_conflict_rationale() -> None:
    facts = build_facts(branch_a_diff=BRANCH_A_DIFF, branch_b_diff=BRANCH_B_DIFF)
    concrete = score_rationale(
        _result(
            "concrete",
            "conflict",
            0.9,
            "`calculate_total` is renamed while `build_report` still calls it; "
            "therefore the merge raises NameError.",
            ["calculate_total", "compute_grand_total", "build_report"],
        ),
        facts,
    )
    speculative = score_rationale(
        _result(
            "speculative",
            "conflict",
            0.9,
            "`calculate_total` might possibly be incompatible and could probably "
            "break `build_report`.",
            ["calculate_total", "compute_grand_total", "build_report"],
        ),
        facts,
    )
    assert concrete.total > speculative.total
    assert speculative.speculation_penalty > 0
