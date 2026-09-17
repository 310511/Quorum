"""Phase 2: filter merges to those touching executable Python code."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from real_world.common import append_jsonl, git_output, load_existing_ids, progress, read_jsonl
from real_world.config import (
    DEPENDENCY_BUMP_FILES,
    FILTERED_JSONL,
    MERGES_JSONL,
    REPO_BY_SLUG,
    SKIP_BASENAMES,
    SKIP_PATH_FRAGMENTS,
    SKIP_PATH_PREFIXES,
    TEST_PATH_MARKERS,
)

logger = logging.getLogger(__name__)

COMMENT_ONLY_RE = re.compile(r"^[\s#+\\-]*$")
DOCSTRING_ONLY_RE = re.compile(r'^[\s+\-]*("""|\'\'\')')


@dataclass
class FilteredMerge:
    id: str
    repository: str
    merge_commit: str
    parent_a: str
    parent_b: str
    merge_base: str
    files_modified: list[str]
    executable_python_files: list[str]
    branch_a_files: list[str]
    branch_b_files: list[str]
    filter_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "repository": self.repository,
            "merge_commit": self.merge_commit,
            "parent_a": self.parent_a,
            "parent_b": self.parent_b,
            "merge_base": self.merge_base,
            "files_modified": self.files_modified,
            "executable_python_files": self.executable_python_files,
            "branch_a_files": self.branch_a_files,
            "branch_b_files": self.branch_b_files,
            "filter_reason": self.filter_reason,
        }


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def is_skip_path(path: str) -> bool:
    normalized = _normalize_path(path).lower()
    basename = Path(normalized).name.lower()
    if basename in SKIP_BASENAMES:
        return True
    for prefix in SKIP_PATH_PREFIXES:
        if normalized.startswith(prefix):
            return True
    for fragment in SKIP_PATH_FRAGMENTS:
        if fragment in f"/{normalized}/":
            return True
    return False


def is_test_path(path: str) -> bool:
    normalized = f"/{_normalize_path(path).lower()}/"
    return any(marker in normalized for marker in TEST_PATH_MARKERS) or normalized.endswith("/conftest.py")


def is_executable_python(path: str) -> bool:
    normalized = _normalize_path(path)
    if not normalized.endswith(".py"):
        return False
    if is_skip_path(normalized):
        return False
    if is_test_path(normalized):
        return False
    return True


def changed_files(repo: Path, base: str, head: str) -> list[str]:
    output = git_output(repo, "diff", "--name-only", base, head)
    if not output:
        return []
    return [_normalize_path(line) for line in output.splitlines() if line.strip()]


def diff_text(repo: Path, base: str, head: str, path: str | None = None) -> str:
    args = ["diff", base, head]
    if path:
        args.extend(["--", path])
    return git_output(repo, *args)


def is_comment_or_formatting_only(diff: str) -> bool:
    """Heuristic: every changed hunk line is whitespace/comment only."""
    if not diff.strip():
        return True
    meaningful = []
    for line in diff.splitlines():
        if line.startswith(("+++", "---", "@@", "diff --git", "index ")):
            continue
        if line.startswith(("+", "-")):
            payload = line[1:]
            if not payload.strip():
                continue
            if payload.strip().startswith("#"):
                continue
            if DOCSTRING_ONLY_RE.match(line):
                continue
            meaningful.append(line)
    return len(meaningful) == 0


def is_dependency_only_change(files: list[str], repo: Path, base: str, head: str) -> bool:
    if not files:
        return True
    if all(Path(f).name in DEPENDENCY_BUMP_FILES for f in files):
        return True
    non_dep = [f for f in files if Path(f).name not in DEPENDENCY_BUMP_FILES]
    if non_dep:
        return False
    combined = diff_text(repo, base, head)
    return is_comment_or_formatting_only(combined)


def filter_merge(record: dict[str, Any]) -> FilteredMerge | None:
    spec = REPO_BY_SLUG.get(record["repository"])
    if spec is None:
        return None
    repo = spec.clone_path
    merge_base = record["merge_base"]
    parent_a = record["parent_a"]
    parent_b = record["parent_b"]

    branch_a_files = changed_files(repo, merge_base, parent_a)
    branch_b_files = changed_files(repo, merge_base, parent_b)
    all_files = sorted(set(branch_a_files) | set(branch_b_files))

    if not all_files:
        return None

    if all(is_skip_path(f) for f in all_files):
        return None

    exec_a = [f for f in branch_a_files if is_executable_python(f)]
    exec_b = [f for f in branch_b_files if is_executable_python(f)]
    executable = sorted(set(exec_a) | set(exec_b))

    if not executable:
        return None

    # Drop merges where executable changes are comment/formatting only.
    exec_diffs = []
    for path in executable:
        exec_diffs.append(diff_text(repo, merge_base, parent_a, path))
        exec_diffs.append(diff_text(repo, merge_base, parent_b, path))
    if all(is_comment_or_formatting_only(d) for d in exec_diffs if d.strip()):
        return None

    only_tests = all(is_test_path(f) for f in all_files)
    if only_tests:
        return None

    if is_dependency_only_change(all_files, repo, merge_base, parent_a) and is_dependency_only_change(
        all_files, repo, merge_base, parent_b
    ):
        return None

    return FilteredMerge(
        id=record["id"],
        repository=record["repository"],
        merge_commit=record["merge_commit"],
        parent_a=parent_a,
        parent_b=parent_b,
        merge_base=merge_base,
        files_modified=all_files,
        executable_python_files=executable,
        branch_a_files=branch_a_files,
        branch_b_files=branch_b_files,
        filter_reason="executable_python",
    )


def filter_all(*, resume: bool = True) -> dict[str, int]:
    merges = read_jsonl(MERGES_JSONL)
    existing = load_existing_ids(FILTERED_JSONL) if resume else set()
    kept = 0
    stats = {"scanned": 0, "kept": 0, "skipped": 0}

    for record in progress(merges, desc="filter merges", total=len(merges)):
        stats["scanned"] += 1
        if record["id"] in existing:
            continue
        filtered = filter_merge(record)
        if filtered is None:
            stats["skipped"] += 1
            continue
        append_jsonl(FILTERED_JSONL, filtered.to_dict())
        existing.add(record["id"])
        kept += 1
        stats["kept"] = kept

    logger.info(
        "Filtered merges: scanned=%d kept=%d skipped=%d",
        stats["scanned"],
        stats["kept"],
        stats["skipped"],
    )
    return stats
