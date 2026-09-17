"""Unit tests for real-world semantic merge dataset pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from real_world.analysis.agreement import cohens_kappa
from real_world.analysis.heuristics import score_heuristics
from real_world.ast.symbol_extractor import parse_python_source
from real_world.ast.symbol_graph import _changed_symbols, detect_intersection
from real_world.filters.initial_filter import (
    is_comment_or_formatting_only,
    is_executable_python,
    is_skip_path,
    is_test_path,
)

LEFT_SRC = """
import helper

def calculate_total(items, tax=0):
    return helper.sum_values(items) + tax
"""

RIGHT_SRC = """
import helper

def process(items):
    return calculate_total(items)
"""

BASE_SRC = """
import helper

def calculate_total(items):
    return helper.sum_values(items)
"""


def test_skip_and_executable_paths():
    assert is_skip_path("README.md")
    assert is_skip_path("docs/guide/index.rst")
    assert is_test_path("tests/test_foo.py")
    assert is_executable_python("src/pkg/module.py")
    assert not is_executable_python("tests/test_foo.py")


def test_comment_only_diff_detection():
    diff = """diff --git a/a.py b/a.py
--- a/a.py
+++ b/a.py
@@ -1,2 +1,2 @@
-# old comment
+# new comment
"""
    assert is_comment_or_formatting_only(diff)


def test_symbol_extraction_and_intersection():
    base = parse_python_source("mod.py", BASE_SRC)
    left = parse_python_source("mod.py", LEFT_SRC)
    right = parse_python_source("mod.py", RIGHT_SRC)
    assert base and left and right

    left_changed = _changed_symbols({"mod.py": base}, {"mod.py": left})
    right_changed = _changed_symbols({"mod.py": base}, {"mod.py": right})
    assert "calculate_total" in left_changed
    assert "process" in right_changed

    intersection = detect_intersection(
        base_symbols={"mod.py": base},
        left_symbols={"mod.py": left},
        right_symbols={"mod.py": right},
        left_files=["mod.py"],
        right_files=["mod.py"],
    )
    assert intersection.intersects
    assert "mod.py" in intersection.shared_files


def test_cohens_kappa_perfect_agreement():
    a = {"1": "conflict", "2": "compatible"}
    b = {"1": "conflict", "2": "compatible"}
    assert cohens_kappa(a, b) == 1.0


def test_heuristics_never_assigns_ground_truth_label_field(tmp_path, monkeypatch):
    from real_world import config

    record = {
        "id": "abc",
        "repository": "requests",
        "merge_base": "base",
        "parent_a": "left",
        "parent_b": "right",
        "affected_symbols": ["calculate_total"],
        "executable_python_files": ["mod.py"],
    }

    class FakeRepo:
        clone_path = tmp_path

    monkeypatch.setitem(config.REPO_BY_SLUG, "requests", FakeRepo())

    def fake_diff(repo, base, head, path=None):
        if head == "left":
            return "+def calculate_total(x, tax=0):\n+    return x\n"
        return "+    return calculate_total(items)\n"

    monkeypatch.setattr("real_world.analysis.heuristics.diff_text", fake_diff)
    scored = score_heuristics(record)
    assert "label" not in scored
    assert scored["heuristic"]["estimated_label"] in {"conflict", "compatible", "uncertain"}
    assert 0.0 <= scored["heuristic"]["confidence"] <= 1.0


def test_parse_merge_commit_skips_unrelated_histories(tmp_path, monkeypatch):
    from real_world.miners import merge_miner as miner
    from real_world.config import RepositorySpec

    spec = RepositorySpec("test", "https://example.com/test", "test")

    def fake_git_output(repo, *args):
        if args[0] == "rev-parse":
            return "aaa bbb"
        if args[0] == "merge-base":
            return None
        if args[0] == "show":
            return "subject line"
        raise AssertionError(args)

    monkeypatch.setattr(miner, "git_output", fake_git_output)
    monkeypatch.setattr(miner, "git_output_optional", lambda repo, *args: None)

    assert miner.parse_merge_commit(tmp_path, "merge123", spec) is None


def test_freeze_requires_human_annotations(tmp_path, monkeypatch):
    from real_world.analysis import freeze as freeze_mod

    candidate_dir = tmp_path / "candidates" / "ex1"
    candidate_dir.mkdir(parents=True)
    (candidate_dir / "metadata.json").write_text(
        json.dumps(
            {
                "id": "ex1",
                "repository": "requests",
                "merge_commit": "m",
                "merge_base": "b",
                "parent_a": "a",
                "parent_b": "c",
                "files_modified": ["mod.py"],
                "affected_symbols": [],
                "semantic_category": "Other",
            }
        ),
        encoding="utf-8",
    )
    (candidate_dir / "left.diff").write_text("diff\n", encoding="utf-8")
    (candidate_dir / "right.diff").write_text("diff\n", encoding="utf-8")

    ann_path = tmp_path / "annotations.jsonl"
    ann_path.write_text(
        json.dumps({"id": "ex1", "label": "conflict", "reason": "stale caller"}) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(freeze_mod, "CANDIDATES_DIR", tmp_path / "candidates")
    monkeypatch.setattr(freeze_mod, "FROZEN_ROOT", tmp_path / "examples")
    monkeypatch.setattr(freeze_mod, "FROZEN_LABELS", tmp_path / "labels.json")
    monkeypatch.setattr(freeze_mod, "FROZEN_METADATA", tmp_path / "metadata.json")
    monkeypatch.setattr(freeze_mod, "FROZEN_README", tmp_path / "README.md")
    monkeypatch.setattr(freeze_mod, "HEURISTICS_JSONL", tmp_path / "heuristics.jsonl")

    stats = freeze_mod.freeze_dataset(annotations_paths=[ann_path])
    assert stats["total_examples"] == 1
    assert (tmp_path / "examples" / "ex1" / "label.json").exists()
