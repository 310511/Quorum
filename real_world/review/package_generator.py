"""Phase 5: materialize candidate packages on disk."""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Any

from real_world.common import progress, read_jsonl
from real_world.config import CANDIDATES_DIR, HEURISTICS_JSONL, REPO_BY_SLUG
from real_world.filters.initial_filter import diff_text

logger = logging.getLogger(__name__)


def _checkout_tree(repo_path: Path, commit: str, dest: Path, files: list[str]) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    from real_world.common import git_output

    for rel_path in files:
        try:
            content = git_output(repo_path, "show", f"{commit}:{rel_path}")
        except Exception:
            continue
        out_path = dest / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")


def write_candidate_package(record: dict[str, Any], dest: Path) -> None:
    spec = REPO_BY_SLUG[record["repository"]]
    repo = spec.clone_path
    merge_base = record["merge_base"]
    parent_a = record["parent_a"]
    parent_b = record["parent_b"]
    exec_files = record.get("executable_python_files", [])

    left_diff = diff_text(repo, merge_base, parent_a)
    right_diff = diff_text(repo, merge_base, parent_b)

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    metadata = {
        "id": record["id"],
        "repository": record["repository"],
        "repository_url": spec.url,
        "merge_commit": record.get("merge_commit"),
        "merge_base": merge_base,
        "parent_a": parent_a,
        "parent_b": parent_b,
        "files_modified": record.get("files_modified", []),
        "executable_python_files": exec_files,
        "affected_symbols": record.get("affected_symbols", []),
        "semantic_category": record.get("semantic_category", "Other"),
        "intersection": record.get("intersection", {}),
        "heuristic": record.get("heuristic", {}),
    }
    (dest / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (dest / "left.diff").write_text(left_diff + ("\n" if left_diff else ""), encoding="utf-8")
    (dest / "right.diff").write_text(right_diff + ("\n" if right_diff else ""), encoding="utf-8")

    changed_symbols = {
        "affected_symbols": record.get("affected_symbols", []),
        "left_changed_symbols": record.get("left_changed_symbols", []),
        "right_changed_symbols": record.get("right_changed_symbols", []),
        "intersection": record.get("intersection", {}),
    }
    (dest / "changed_symbols.json").write_text(
        json.dumps(changed_symbols, indent=2) + "\n", encoding="utf-8"
    )

    base_dir = dest / "base"
    _checkout_tree(repo, merge_base, base_dir, exec_files)
    _checkout_tree(repo, parent_a, dest / "branch_a", exec_files)
    _checkout_tree(repo, parent_b, dest / "branch_b", exec_files)

    heuristic = record.get("heuristic", {})
    summary_lines = [
        f"# Candidate `{record['id']}`",
        "",
        f"- **Repository:** {record['repository']}",
        f"- **Merge commit:** `{record.get('merge_commit')}`",
        f"- **Merge base:** `{merge_base}`",
        f"- **Parent A:** `{parent_a}`",
        f"- **Parent B:** `{parent_b}`",
        f"- **Category:** {record.get('semantic_category', 'Other')}",
        "",
        "## Affected symbols",
        "",
    ]
    for sym in record.get("affected_symbols", [])[:30]:
        summary_lines.append(f"- `{sym}`")
    if len(record.get("affected_symbols", [])) > 30:
        summary_lines.append(f"- … and {len(record['affected_symbols']) - 30} more")

    summary_lines.extend(
        [
            "",
            "## Heuristic estimate (NOT ground truth)",
            "",
            f"- **Estimated label:** {heuristic.get('estimated_label', 'uncertain')}",
            f"- **Confidence:** {heuristic.get('confidence', 0):.2f}",
            f"- **Reason:** {heuristic.get('reason', 'n/a')}",
            "",
            "## Intersection reasons",
            "",
        ]
    )
    for reason in record.get("intersection", {}).get("reasons", []):
        summary_lines.append(f"- {reason}")

    (dest / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")


def generate_packages(*, source_jsonl: Path | None = None, limit: int | None = None) -> int:
    source = source_jsonl or HEURISTICS_JSONL
    records = read_jsonl(source)
    if limit:
        records = records[:limit]
    CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for record in progress(records, desc="package candidates", total=len(records)):
        dest = CANDIDATES_DIR / record["id"]
        write_candidate_package(record, dest)
        count += 1

    logger.info("Wrote %d candidate packages to %s", count, CANDIDATES_DIR)
    return count
