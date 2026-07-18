"""Tests for self-generated dataset validation."""

import json

from quorum.dataset import audit_records
from quorum.generate_pairs import generate_verified_pairs


def _record(kind: str, patch: str, test: str, **extra):
    record = {
        "kind": kind,
        "candidate": {"patch": patch},
        "labels": {"final": "positive", "manual": "pending", "test": test},
    }
    record.update(extra)
    return record


def test_empty_ollama_candidate_is_rejected():
    record = _record(
        "agent_candidate",
        "",
        "pass",
        generator={"files_applied": 0},
    )
    audit = audit_records([record])
    assert audit.usable_agent_records == 0
    assert audit.rejection_reasons == {"agent_applied_no_files": 1}


def test_two_nonempty_agent_branches_form_candidate_pair():
    common = {
        "repository": "repo",
        "merge_base": "abc123",
        "pair_id": "pair-1",
    }
    records = [
        _record("agent_candidate", "diff-a", "pass", **common),
        _record("agent_candidate", "diff-b", "pass", **common),
    ]
    audit = audit_records(records)
    assert audit.usable_agent_records == 2
    assert audit.candidate_agent_pairs == 1


def test_synthetic_failure_is_kept_as_single_patch_example():
    record = _record(
        "synthetic_mutation",
        "diff",
        "fail",
        mutation={"name": "signature_break", "expected_label": "negative"},
    )
    record["labels"]["final"] = "negative"
    audit = audit_records([record])
    assert audit.usable_synthetic_records == 1
    assert audit.candidate_agent_pairs == 0


def test_generate_verified_rename_pair(tmp_path):
    source = tmp_path / "fixture"
    source.mkdir()
    (source / "calculator.py").write_text(
        "def add(left, right):\n    return left + right\n", encoding="utf-8"
    )
    (source / "test_calculator.py").write_text(
        "import unittest\n"
        "from calculator import add\n\n"
        "class CalculatorTests(unittest.TestCase):\n"
        "    def test_add(self):\n"
        "        self.assertEqual(add(2, 3), 5)\n",
        encoding="utf-8",
    )
    records = tmp_path / "records.jsonl"
    records.write_text(
        json.dumps(
            {
                "kind": "baseline",
                "record_id": "baseline-1",
                "repository": str(source),
                "merge_base": "abc123",
                "candidate": {"patch": ""},
                "labels": {"final": "positive", "test": "pass"},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    generated = generate_verified_pairs(records, tmp_path / "pairs", limit=1)

    assert len(generated) == 1
    pair = tmp_path / "pairs" / generated[0].name
    label = json.loads((pair / "label.json").read_text(encoding="utf-8"))
    assert label["ground_truth"] == "conflict"
    assert label["validation"]["branch_a_tests"] == "pass"
    assert label["validation"]["branch_b_tests"] == "pass"
    assert label["validation"]["merged_tests"] == "fail"
