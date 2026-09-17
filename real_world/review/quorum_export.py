"""Export real-world candidates as Quorum-evaluable pair directories."""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Any

from real_world.common import git_output, progress
from real_world.config import CANDIDATES_DIR, FROZEN_ROOT, REAL_WORLD_ROOT
from real_world.config import REPO_BY_SLUG

logger = logging.getLogger(__name__)


def _checkout_tree(repo_path: Path, commit: str, dest: Path, files: list[str]) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for rel_path in files:
        try:
            content = git_output(repo_path, "show", f"{commit}:{rel_path}")
        except Exception:
            continue
        out_path = dest / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")


def materialize_quorum_pair(
    candidate_dir: Path,
    dest_dir: Path,
    *,
    annotation: dict[str, Any] | None = None,
) -> None:
    """Write a full Quorum pair layout (diffs + merge_base + branch_a + branch_b)."""
    meta = json.loads((candidate_dir / "metadata.json").read_text(encoding="utf-8"))
    spec = REPO_BY_SLUG[meta["repository"]]
    repo = spec.clone_path
    exec_files = meta.get("executable_python_files") or meta.get("files_modified") or []

    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True)

    shutil.copy2(candidate_dir / "left.diff", dest_dir / "branch_a.diff")
    shutil.copy2(candidate_dir / "right.diff", dest_dir / "branch_b.diff")

    _checkout_tree(repo, meta["merge_base"], dest_dir / "merge_base", exec_files)
    _checkout_tree(repo, meta["parent_a"], dest_dir / "branch_a", exec_files)
    _checkout_tree(repo, meta["parent_b"], dest_dir / "branch_b", exec_files)

    if (candidate_dir / "summary.md").exists():
        shutil.copy2(candidate_dir / "summary.md", dest_dir / "context.md")
    if (candidate_dir / "changed_symbols.json").exists():
        shutil.copy2(candidate_dir / "changed_symbols.json", dest_dir / "changed_symbols.json")

    heuristic = meta.get("heuristic", {})
    label_payload: dict[str, Any] = {
        "language": "python",
        "semantic_category": meta.get("semantic_category"),
        "repository": meta.get("repository"),
        "merge_commit": meta.get("merge_commit"),
        "merge_base": meta.get("merge_base"),
        "parent_a": meta.get("parent_a"),
        "parent_b": meta.get("parent_b"),
        "notes": meta.get("notes", ""),
    }

    if annotation and annotation.get("label") in {"conflict", "compatible"}:
        label_payload["ground_truth"] = (
            "conflict" if annotation["label"] == "conflict" else "compatible"
        )
        label_payload["notes"] = annotation.get("reason") or annotation.get("explanation") or ""
    else:
        label_payload["ground_truth"] = None
        label_payload["review_status"] = "pending"
        label_payload["heuristic_estimate"] = heuristic.get("estimated_label")
        label_payload["notes"] = (
            label_payload.get("notes")
            or heuristic.get("reason")
            or "Pending human review — no ground-truth label assigned."
        )

    (dest_dir / "label.json").write_text(json.dumps(label_payload, indent=2) + "\n", encoding="utf-8")
    (dest_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def _load_annotations() -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for name in ("annotations.jsonl", "reviewer_A.jsonl", "reviewer_B.jsonl"):
        path = REAL_WORLD_ROOT / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            example_id = row.get("id")
            if example_id and row.get("label") in {"conflict", "compatible"}:
                merged[str(example_id)] = row
    return merged


def materialize_examples(
    *,
    dest: Path | None = None,
    candidates_dir: Path | None = None,
    only_annotated: bool = False,
) -> dict[str, int]:
    """Export candidate packages to Quorum pair directories."""
    dest = dest or FROZEN_ROOT
    candidates_dir = candidates_dir or CANDIDATES_DIR
    if not candidates_dir.is_dir():
        raise FileNotFoundError(
            f"candidates directory not found: {candidates_dir}\n"
            "Run: real-world-pipeline packages"
        )

    annotations = _load_annotations()
    candidate_dirs = sorted(p for p in candidates_dir.iterdir() if p.is_dir())
    if not candidate_dirs:
        raise FileNotFoundError(
            f"no candidate packages in {candidates_dir}\n"
            "Run: real-world-pipeline run-all (or packages)"
        )

    dest.mkdir(parents=True, exist_ok=True)
    exported = 0
    skipped = 0

    for candidate_dir in progress(candidate_dirs, desc="materialize examples", total=len(candidate_dirs)):
        example_id = candidate_dir.name
        if only_annotated and example_id not in annotations:
            skipped += 1
            continue
        materialize_quorum_pair(
            candidate_dir,
            dest / example_id,
            annotation=annotations.get(example_id),
        )
        exported += 1

    logger.info("Materialized %d examples -> %s (skipped %d)", exported, dest, skipped)
    return {"exported": exported, "skipped": skipped, "dest": str(dest)}
