"""Generate verified, textually clean semantic-conflict pairs."""

from __future__ import annotations

import ast
import difflib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from quorum.dataset import load_jsonl


@dataclass(frozen=True)
class GeneratedPair:
    name: str
    source_repository: str
    symbol: str


def _copy_source(source: Path, destination: Path) -> None:
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "*.pyc"),
    )


def _source_module(root: Path) -> tuple[Path, str] | None:
    candidates = sorted(
        path
        for path in root.glob("*.py")
        if not path.name.startswith("test_") and path.name != "helpers.py"
    )
    for path in candidates:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    return path, node.name
    return None


def _replace_symbol(text: str, old: str, new: str) -> str:
    return re.sub(rf"\b{re.escape(old)}\b", new, text)


def _branch_a_files(source: Path, symbol: str) -> dict[str, str]:
    renamed = f"{symbol}_v2"
    changed: dict[str, str] = {}
    for path in sorted(source.rglob("*.py")):
        if any(part in {".git", "__pycache__"} for part in path.parts):
            continue
        original = path.read_text(encoding="utf-8")
        updated = _replace_symbol(original, symbol, renamed)
        if updated != original:
            changed[path.relative_to(source).as_posix()] = updated
    return changed


def _branch_b_files(module: Path, symbol: str, pair_slug: str) -> dict[str, str]:
    consumer_module = f"quorum_consumer_{pair_slug}"
    consumer_path = f"{consumer_module}.py"
    test_path = f"test_{consumer_module}.py"
    module_name = module.stem
    return {
        consumer_path: (
            f'"""Independent caller added by Branch B."""\n\n'
            f"from {module_name} import {symbol}\n\n\n"
            f"def call_original(*args, **kwargs):\n"
            f"    return {symbol}(*args, **kwargs)\n"
        ),
        test_path: (
            "import unittest\n\n"
            f"from {consumer_module} import call_original\n\n\n"
            f"class {pair_slug.title().replace('_', '')}Tests(unittest.TestCase):\n"
            "    def test_consumer_is_available(self):\n"
            "        self.assertTrue(callable(call_original))\n\n\n"
            'if __name__ == "__main__":\n'
            "    unittest.main()\n"
        ),
    }


def _overlay(root: Path, files: dict[str, str]) -> None:
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _tests_pass(source: Path, files: dict[str, str]) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix="quorum-pair-") as temp:
        worktree = Path(temp) / "repo"
        _copy_source(source, worktree)
        _overlay(worktree, files)
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover"],
            cwd=worktree,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output


def _diff(source: Path, files: dict[str, str]) -> str:
    chunks: list[str] = []
    for rel, content in sorted(files.items()):
        original_path = source / rel
        original = (
            original_path.read_text(encoding="utf-8").splitlines(keepends=True)
            if original_path.exists()
            else []
        )
        updated = content.splitlines(keepends=True)
        chunks.append(
            "".join(
                difflib.unified_diff(
                    original,
                    updated,
                    fromfile=f"a/{rel}",
                    tofile=f"b/{rel}",
                )
            )
        )
    return "\n".join(chunk.rstrip() for chunk in chunks if chunk).strip()


def _write_pair(
    destination: Path,
    source: Path,
    module: Path,
    symbol: str,
    branch_a: dict[str, str],
    branch_b: dict[str, str],
    baseline_record: dict[str, Any],
    merged_output: str,
) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    _copy_source(source, destination / "merge_base")
    _overlay(destination / "branch_a", branch_a)
    _overlay(destination / "branch_b", branch_b)
    (destination / "branch_a.diff").write_text(_diff(source, branch_a), encoding="utf-8")
    (destination / "branch_b.diff").write_text(_diff(source, branch_b), encoding="utf-8")
    renamed = f"{symbol}_v2"
    context = (
        "# Self-generated semantic conflict\n\n"
        f"- Source fixture: `{source}`\n"
        f"- Branch A renames `{symbol}` to `{renamed}` and updates existing callers.\n"
        f"- Branch B independently adds a new caller of `{symbol}` in a new file.\n"
        "- Each branch passes tests independently and their file changes do not overlap.\n"
        "- The merged tree fails because Branch B retains the removed symbol.\n"
    )
    (destination / "context.md").write_text(context, encoding="utf-8")
    label = {
        "ground_truth": "conflict",
        "language": "python",
        "source": "self_generated_verified",
        "conflict_type": "rename_stale_reference",
        "notes": f"{symbol} renamed to {renamed} while Branch B adds a stale caller",
        "validation": {
            "branch_a_tests": "pass",
            "branch_b_tests": "pass",
            "merged_tests": "fail",
            "merged_test_output": merged_output[-2000:],
        },
    }
    (destination / "label.json").write_text(
        json.dumps(label, indent=2) + "\n", encoding="utf-8"
    )
    meta = {
        "baseline_record_id": baseline_record.get("record_id"),
        "merge_base": baseline_record.get("merge_base"),
        "source_repository": str(source),
        "source_module": module.relative_to(source).as_posix(),
        "symbol": symbol,
    }
    (destination / "meta.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )


def generate_verified_pairs(
    records_path: Path,
    destination: Path,
    limit: int = 10,
) -> list[GeneratedPair]:
    """Create rename/stale-reference pairs and verify all three test states."""
    records = load_jsonl(records_path)
    baselines = [record for record in records if record.get("kind") == "baseline"]
    generated: list[GeneratedPair] = []
    seen_repositories: set[str] = set()

    for record in baselines:
        repository = str(record.get("repository") or "")
        if not repository or repository in seen_repositories:
            continue
        seen_repositories.add(repository)
        source = Path(repository)
        if not source.is_dir():
            continue
        selected = _source_module(source)
        if selected is None:
            continue
        module, symbol = selected
        slug = re.sub(r"[^a-z0-9]+", "_", source.name.lower()).strip("_")
        pair_name = f"self_{slug}_rename_stale"
        branch_a = _branch_a_files(source, symbol)
        branch_b = _branch_b_files(module, symbol, slug)
        if not branch_a:
            continue

        a_passed, _ = _tests_pass(source, branch_a)
        b_passed, _ = _tests_pass(source, branch_b)
        merged_passed, merged_output = _tests_pass(source, branch_a | branch_b)
        if not a_passed or not b_passed or merged_passed:
            continue

        _write_pair(
            Path(destination) / pair_name,
            source,
            module,
            symbol,
            branch_a,
            branch_b,
            record,
            merged_output,
        )
        generated.append(
            GeneratedPair(
                name=pair_name,
                source_repository=repository,
                symbol=symbol,
            )
        )
        if len(generated) >= limit:
            break
    return generated
