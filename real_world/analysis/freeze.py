"""Phase 10: freeze annotated examples into publication dataset."""

from __future__ import annotations

import json
import logging
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from real_world.common import read_jsonl, write_json
from real_world.config import (
    CANDIDATES_DIR,
    FROZEN_LABELS,
    FROZEN_METADATA,
    FROZEN_README,
    FROZEN_ROOT,
    HEURISTICS_JSONL,
    REAL_WORLD_ROOT,
    REPOSITORIES,
    SEMANTIC_CATEGORIES,
)
from real_world.config import REPO_BY_SLUG

logger = logging.getLogger(__name__)


def _load_annotations(*paths: Path) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for path in paths:
        if not path.exists():
            continue
        for row in read_jsonl(path):
            example_id = row.get("id") or row.get("example_id")
            label = row.get("label")
            if not example_id or label not in {"conflict", "compatible"}:
                continue
            merged[str(example_id)] = row
    return merged


def _quorum_label(label: str) -> str:
    return "conflict" if label == "conflict" else "compatible"


def freeze_dataset(
    *,
    annotations_paths: list[Path] | None = None,
    require_dual_agreement: bool = False,
    reviewer_a: Path | None = None,
    reviewer_b: Path | None = None,
) -> dict[str, Any]:
    annotations_paths = annotations_paths or [
        REAL_WORLD_ROOT / "annotations.jsonl",
        REAL_WORLD_ROOT / "reviewer_A.jsonl",
        REAL_WORLD_ROOT / "reviewer_B.jsonl",
    ]
    annotations = _load_annotations(*annotations_paths)

    if require_dual_agreement and reviewer_a and reviewer_b:
        a = {r["id"]: r["label"] for r in read_jsonl(reviewer_a) if r.get("label") in {"conflict", "compatible"}}
        b = {r["id"]: r["label"] for r in read_jsonl(reviewer_b) if r.get("label") in {"conflict", "compatible"}}
        agreed = {i for i in set(a) & set(b) if a[i] == b[i]}
        annotations = {i: annotations[i] for i in agreed if i in annotations}

    heuristics = {r["id"]: r for r in read_jsonl(HEURISTICS_JSONL)}
    if FROZEN_ROOT.exists():
        shutil.rmtree(FROZEN_ROOT)
    FROZEN_ROOT.mkdir(parents=True, exist_ok=True)

    labels: dict[str, Any] = {}
    examples: list[dict[str, Any]] = []

    for example_id, ann in sorted(annotations.items()):
        candidate_dir = CANDIDATES_DIR / example_id
        if not candidate_dir.exists():
            logger.warning("Missing candidate package for %s — skipped", example_id)
            continue

        meta_path = candidate_dir / "metadata.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        heuristic = heuristics.get(example_id, {})
        label = ann["label"]
        explanation = ann.get("reason") or ann.get("explanation") or ""

        dest = FROZEN_ROOT / example_id
        dest.mkdir(parents=True, exist_ok=True)

        # Quorum-compatible layout
        shutil.copy2(candidate_dir / "left.diff", dest / "branch_a.diff")
        shutil.copy2(candidate_dir / "right.diff", dest / "branch_b.diff")
        if (candidate_dir / "base").exists():
            shutil.copytree(candidate_dir / "base", dest / "merge_base")
        for branch in ("branch_a", "branch_b"):
            src = candidate_dir / branch
            if src.exists():
                shutil.copytree(src, dest / branch)
        if (candidate_dir / "changed_symbols.json").exists():
            shutil.copy2(candidate_dir / "changed_symbols.json", dest / "changed_symbols.json")

        label_payload = {
            "ground_truth": _quorum_label(label),
            "notes": explanation,
            "semantic_category": meta.get("semantic_category"),
            "repository": meta.get("repository"),
            "merge_commit": meta.get("merge_commit"),
        }
        (dest / "label.json").write_text(json.dumps(label_payload, indent=2) + "\n", encoding="utf-8")

        example_record = {
            "id": example_id,
            "repository": meta.get("repository"),
            "merge_commit": meta.get("merge_commit"),
            "merge_base": meta.get("merge_base"),
            "parent_a": meta.get("parent_a"),
            "parent_b": meta.get("parent_b"),
            "files_modified": meta.get("files_modified", []),
            "affected_symbols": meta.get("affected_symbols", []),
            "semantic_category": meta.get("semantic_category"),
            "label": label,
            "explanation": explanation,
            "annotator": ann.get("reviewer") or ann.get("annotator"),
            "estimated_label": heuristic.get("heuristic", {}).get("estimated_label"),
        }
        examples.append(example_record)
        labels[example_id] = label_payload

    stats = {
        "total_examples": len(examples),
        "conflict": sum(1 for e in examples if e["label"] == "conflict"),
        "compatible": sum(1 for e in examples if e["label"] == "compatible"),
        "by_repository": dict(Counter(e["repository"] for e in examples)),
        "by_category": dict(Counter(e["semantic_category"] for e in examples)),
        "frozen_at": datetime.now(timezone.utc).isoformat(),
    }

    write_json(FROZEN_LABELS, labels)
    metadata = {
        "statistics": stats,
        "repositories": [r.slug for r in REPOSITORIES],
        "semantic_categories": list(SEMANTIC_CATEGORIES),
        "examples": examples,
    }
    write_json(FROZEN_METADATA, metadata)
    _write_readme(stats)
    logger.info("Frozen %d examples into %s", len(examples), FROZEN_ROOT)
    return stats


def _write_readme(stats: dict[str, Any]) -> None:
    repos = "\n".join(f"- `{r.url}`" for r in REPOSITORIES)
    cats = ", ".join(SEMANTIC_CATEGORIES)
    content = f"""# Real-world semantic merge benchmark

Frozen dataset for evaluating **semantic** (not textual) merge conflict detection.

## Statistics

- Total examples: **{stats['total_examples']}**
- Semantic conflicts: **{stats['conflict']}**
- Semantic compatibles: **{stats['compatible']}**

## Repositories

{repos}

## Generation process

1. Mine all merge commits from target repositories (`real_world/miners/merge_miner.py`)
2. Filter to merges touching executable Python (`real_world/filters/initial_filter.py`)
3. Detect AST symbol-graph intersections (`real_world/ast/candidate_detector.py`)
4. Classify semantic category (`real_world/analysis/classifier.py`)
5. Materialize candidate packages (`real_world/review/package_generator.py`)
6. Score conflict heuristics — **no automatic ground truth** (`real_world/analysis/heuristics.py`)
7. Human review via web UI (`real_world/review/annotation_server.py`)
8. Dual-reviewer agreement (`real_world/analysis/agreement.py`)
9. Freeze annotated subset into Quorum pair layout (`real_world/analysis/freeze.py`)

## Filtering

Excluded: README/docs-only, tests-only, CI, translations, dependency-only bumps,
comment/formatting-only diffs. Kept merges where both branches intersect on Python
symbols, shared files, or caller/callee relationships.

## Annotation protocol

Reviewers label each candidate **conflict**, **compatible**, or **skip** with a
written rationale. Ground-truth labels are never inferred by LLMs — only human
annotations (or dual-reviewer agreement when configured) are frozen.

## Semantic categories

{cats}

## Reproducibility

Every example includes commit SHAs (`merge_commit`, `parent_a`, `parent_b`,
`merge_base`) and can be regenerated from git history.
"""
    FROZEN_README.write_text(content, encoding="utf-8")
