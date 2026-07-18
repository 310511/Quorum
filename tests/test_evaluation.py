"""Tests for structured extraction, verdict parsing, and scorecards."""

from __future__ import annotations

import json

import pytest

from quorum.extract import extract_functions, extract_module_summary
from quorum.metrics import score_evaluation
from quorum.models import _parse_verdict_json, normalize_verdict


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("conflict", "conflict"),
        ("semantic_conflict", "conflict"),
        ("incompatible", "conflict"),
        ("incorrect", "conflict"),
        ("bug", "conflict"),
        ("breaking_change", "conflict"),
        ("likely_incorrect", "conflict"),
        ("semantically incorrect", "conflict"),
        ("no_conflict", "no_conflict"),
        ("compatible", "no_conflict"),
        ("safe", "no_conflict"),
    ],
)
def test_verdict_synonyms_are_canonical(raw, expected):
    assert normalize_verdict(raw) == expected


def test_parser_preserves_original_verdict_and_accepts_extra_text():
    raw = json.dumps(
        {
            "verdict": "breaking_change",
            "confidence": 0.8,
            "evidence": ["API changed"],
        }
    ) + "\nextra model text"
    parsed = _parse_verdict_json(raw)
    assert parsed.verdict == "conflict"
    assert parsed.original_verdict == "breaking_change"
    assert parsed.reasoning == "No reasoning provided by model."


def test_structured_extraction_is_deterministic_and_preserves_semantics():
    source = """
import os

VALUE = 1

@staticmethod
def compute(value: int) -> int:
    if value > VALUE:
        return os.path.getsize("x")
    return VALUE
""".strip()
    first = [item.to_dict() for item in extract_functions(source, "sample.py")]
    second = [item.to_dict() for item in extract_functions(source, "sample.py")]
    assert first == second
    assert first[0]["signature"] == "def compute(value: int) -> int:"
    assert "getsize" in first[0]["calls"]
    assert "if_statement:1" in first[0]["control_flow"]
    assert "return_statement:2" in first[0]["control_flow"]
    summary = extract_module_summary(source)
    assert summary["imports"] == ["import os"]
    assert "VALUE" in summary["identifiers"]


def _model_result(model: str, verdict: str, latency: float = 1.0) -> dict:
    return {
        "model_name": model,
        "outcome": "ok",
        "elapsed_seconds": latency,
        "verdict": {
            "verdict": verdict,
            "original_verdict": verdict,
            "confidence": 0.9,
            "reasoning": "reason",
            "evidence": [],
        },
    }


def test_scorecard_includes_majority_committee_and_agreement():
    rows = [
        {
            "ground_truth": "conflict",
            "baseline_verdict": "conflict",
            "committee_verdict": "escalate",
            "baseline": {"wall_clock_seconds": 2.0},
            "committee": {
                "wall_clock_seconds": 3.0,
                "model_results": [
                    _model_result("a", "conflict"),
                    _model_result("b", "conflict"),
                    _model_result("c", "no_conflict"),
                ],
            },
        }
    ]
    scores = score_evaluation(rows)
    assert scores["baseline"]["accuracy"] == 1.0
    assert scores["majority_vote"]["accuracy"] == 1.0
    assert scores["committee"]["escalation_rate"] == 1.0
    assert scores["committee"]["coverage"] == 0.0
    assert scores["individual_models"]["a"]["f1"] == 1.0
    assert scores["per_model_agreement"]["a__b"]["rate"] == 1.0
