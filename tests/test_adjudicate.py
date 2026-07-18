"""Tests for identifier-based evidence overlap adjudication."""

from __future__ import annotations

from quorum.adjudicate import adjudicate, extract_identifiers
from quorum.models import ModelResult, VerdictResponse


def _result(model: str, verdict: str, evidence: list[str], reasoning: str = "") -> ModelResult:
    return ModelResult(
        model_name=model,
        role="test",
        outcome="ok",
        verdict=VerdictResponse(
            verdict=verdict,  # type: ignore[arg-type]
            original_verdict=verdict,
            confidence=0.9,
            reasoning=reasoning or "test reasoning",
            evidence=evidence,
        ),
    )


def test_extract_identifiers_finds_symbols():
    text = "Branch A renames `calculate_total` to `compute_total` in utils.py"
    ids = extract_identifiers(text)
    assert "calculate_total" in ids
    assert "compute_total" in ids


def test_unanimous_conflict_with_shared_identifiers_resolves():
    diff_a = "-def calculate_total(items):\n+def compute_total(items):"
    diff_b = "+from utils import calculate_total"
    results = [
        _result(
            "gemma",
            "conflict",
            [
                "Branch A renames 'calculate_total' to 'compute_total' in utils.py",
                "Branch B imports calculate_total from utils.py",
            ],
        ),
        _result(
            "qwen",
            "conflict",
            [
                "Branch A changes `calculate_total` to `compute_total`",
                "Branch B uses `calculate_total` in finalize_order",
            ],
        ),
        _result("llama", "conflict", ["Branch A diff", "Branch B diff"]),
    ]
    out = adjudicate(results, branch_a_diff=diff_a, branch_b_diff=diff_b)
    assert out.final_verdict == "conflict"
    assert "calculate_total" in out.shared_evidence
    assert "compute_total" in out.shared_evidence
    assert "llama" in out.weak_evidence_models


def test_split_verdict_still_escalates():
    results = [
        _result("gemma", "no_conflict", ["guid type added"], reasoning="orthogonal"),
        _result("qwen", "conflict", ["guid", "hash_sha256"], reasoning="both add types"),
        _result("llama", "conflict", ["hash_sha256", "guid"], reasoning="same file"),
    ]
    diff = "+guid = Regex(...)\n+hash_sha256 = Regex(...)"
    out = adjudicate(results, branch_a_diff=diff, branch_b_diff=diff)
    assert out.final_verdict == "escalate"
    assert out.dissenting_models == ["gemma"]
