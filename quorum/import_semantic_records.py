"""Import schema-v2 semantic_conflict records into Quorum pair directories."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from quorum.dataset import load_jsonl


def _slug(record: dict[str, Any], index: int) -> str:
    conflict = record.get("conflict") or {}
    family = str(conflict.get("family") or "semantic")
    family = re.sub(r"[^a-z0-9_]+", "_", family.lower()).strip("_") or "semantic"
    repo = Path(str(record.get("repository") or ""))
    repo_tail = re.sub(r"[^a-z0-9_]+", "_", repo.name.lower()).strip("_")
    if repo_tail:
        return f"hard_{repo_tail}"
    return f"hard_{family}_{index:04d}"


def _git_archive(repo: Path, commit: str, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as tmp:
        archive_path = Path(tmp.name)
    try:
        with archive_path.open("wb") as fh:
            subprocess.run(
                ["git", "-C", str(repo), "archive", commit],
                check=True,
                stdout=fh,
                stderr=subprocess.PIPE,
            )
        shutil.unpack_archive(archive_path, destination)
    finally:
        archive_path.unlink(missing_ok=True)


def _apply_patch(tree: Path, patch: str) -> None:
    normalized = patch
    if not normalized.endswith("\n"):
        normalized += "\n"
    result = subprocess.run(
        ["git", "apply", "--whitespace=nowarn", "-"],
        cwd=tree,
        input=normalized.encode("utf-8"),
        capture_output=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).decode("utf-8", errors="replace")
        raise RuntimeError(f"git apply failed in {tree}: {detail}")


def _file_map(root: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        mapping[path.relative_to(root).as_posix()] = path.read_text(encoding="utf-8")
    return mapping


def _overlay(base: dict[str, str], branch: dict[str, str]) -> dict[str, str]:
    changed: dict[str, str] = {}
    for rel, content in branch.items():
        if base.get(rel) != content:
            changed[rel] = content
    for rel in base:
        if rel not in branch:
            # Deletion: represent as empty overlay marker file is not supported;
            # Quorum pairs expect present content for changed paths.
            continue
    return changed


def _write_tree(destination: Path, files: dict[str, str]) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    for rel, content in files.items():
        path = destination / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def materialize_record(record: dict[str, Any], destination: Path) -> Path:
    """Write one semantic_conflict record as a Quorum pair folder."""
    if record.get("kind") != "semantic_conflict":
        raise ValueError(f"expected kind=semantic_conflict, got {record.get('kind')!r}")

    repo = Path(str(record["repository"]))
    if not repo.is_dir():
        raise FileNotFoundError(f"repository not found: {repo}")

    merge_base = str(record["merge_base"])
    parents = record.get("parents") or {}
    left = parents.get("left") or {}
    right = parents.get("right") or {}
    left_patch = str(left.get("patch") or "")
    right_patch = str(right.get("patch") or "")
    if not left_patch or not right_patch:
        raise ValueError("record is missing parents.left/right.patch")

    with tempfile.TemporaryDirectory(prefix="quorum-semantic-") as tmp:
        tmp_path = Path(tmp)
        base_dir = tmp_path / "base"
        left_dir = tmp_path / "left"
        right_dir = tmp_path / "right"
        _git_archive(repo, merge_base, base_dir)
        shutil.copytree(base_dir, left_dir)
        shutil.copytree(base_dir, right_dir)
        _apply_patch(left_dir, left_patch)
        _apply_patch(right_dir, right_patch)

        base_files = _file_map(base_dir)
        left_files = _file_map(left_dir)
        right_files = _file_map(right_dir)
        left_overlay = _overlay(base_files, left_files)
        right_overlay = _overlay(base_files, right_files)

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    _write_tree(destination / "merge_base", base_files)
    _write_tree(destination / "branch_a", left_overlay)
    _write_tree(destination / "branch_b", right_overlay)
    _write_tree(destination / "branch_a_full", left_files)
    _write_tree(destination / "branch_b_full", right_files)

    (destination / "branch_a.diff").write_text(left_patch.rstrip() + "\n", encoding="utf-8")
    (destination / "branch_b.diff").write_text(right_patch.rstrip() + "\n", encoding="utf-8")

    conflict = record.get("conflict") or {}
    labels = record.get("labels") or {}
    oracle = record.get("semantic_oracle") or {}
    ground_truth = "conflict" if labels.get("final") == "negative" else "no_conflict"

    context = (
        "# Hard semantic conflict (records1)\n\n"
        f"- Family: `{conflict.get('family')}`\n"
        f"- Difficulty: `{record.get('difficulty')}`\n"
        f"- Description: {conflict.get('description')}\n"
        f"- Hidden invariant: {conflict.get('hidden_invariant')}\n"
        f"- Left intent: {left.get('intent')}\n"
        f"- Right intent: {right.get('intent')}\n"
        f"- Record id: `{record.get('record_id')}`\n"
    )
    (destination / "context.md").write_text(context, encoding="utf-8")

    label = {
        "ground_truth": ground_truth,
        "language": "python",
        "source": "records1_semantic_conflict",
        "conflict_type": conflict.get("family"),
        "difficulty": record.get("difficulty"),
        "record_id": record.get("record_id"),
        "notes": conflict.get("description"),
        "hidden_invariant": conflict.get("hidden_invariant"),
        "surface_characteristics": conflict.get("surface_characteristics"),
        "validation": {
            "compile": labels.get("compile"),
            "public_tests": labels.get("test"),
            "semantic_oracle": labels.get("semantic_oracle"),
            "final": labels.get("final"),
            "oracle_command": oracle.get("command"),
            "oracle_exit_code": oracle.get("exit_code"),
        },
    }
    (destination / "label.json").write_text(
        json.dumps(label, indent=2) + "\n", encoding="utf-8"
    )
    (destination / "meta.json").write_text(
        json.dumps(
            {
                "record_id": record.get("record_id"),
                "repository": str(record.get("repository")),
                "merge_base": merge_base,
                "parents": {
                    "left": {
                        "commit": left.get("commit"),
                        "intent": left.get("intent"),
                        "patch_sha256": left.get("patch_sha256"),
                    },
                    "right": {
                        "commit": right.get("commit"),
                        "intent": right.get("intent"),
                        "patch_sha256": right.get("patch_sha256"),
                    },
                },
                "kind": "semantic_conflict",
                "schema_version": record.get("schema_version"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return destination


def import_semantic_records(
    records_path: Path,
    destination: Path,
    *,
    limit: int | None = None,
) -> list[str]:
    """Import semantic_conflict JSONL records into pair folders. Returns pair names."""
    records = load_jsonl(records_path)
    destination.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    index = 0
    for record in records:
        if record.get("kind") != "semantic_conflict":
            continue
        index += 1
        if limit is not None and len(created) >= limit:
            break
        name = _slug(record, index)
        materialize_record(record, destination / name)
        created.append(name)
    return created
