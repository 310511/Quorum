"""Phase 3: semantic candidate detection via AST symbol intersection."""

from __future__ import annotations

import logging
from typing import Any

from real_world.ast.symbol_extractor import extract_symbols_at_commit
from real_world.ast.symbol_graph import _changed_symbols, build_graph, detect_intersection
from real_world.common import append_jsonl, load_existing_ids, progress, read_jsonl
from real_world.config import CANDIDATES_JSONL, FILTERED_JSONL

logger = logging.getLogger(__name__)


def analyze_candidate(record: dict[str, Any]) -> dict[str, Any] | None:
    repository = record["repository"]
    merge_base = record["merge_base"]
    parent_a = record["parent_a"]
    parent_b = record["parent_b"]
    exec_files = record["executable_python_files"]

    base_symbols = extract_symbols_at_commit(repository, merge_base, exec_files)
    left_symbols = extract_symbols_at_commit(repository, parent_a, exec_files)
    right_symbols = extract_symbols_at_commit(repository, parent_b, exec_files)

    intersection = detect_intersection(
        base_symbols=base_symbols,
        left_symbols=left_symbols,
        right_symbols=right_symbols,
        left_files=[f for f in record["branch_a_files"] if f in exec_files],
        right_files=[f for f in record["branch_b_files"] if f in exec_files],
    )
    if not intersection.intersects:
        return None

    left_changed = sorted(_changed_symbols(base_symbols, left_symbols))
    right_changed = sorted(_changed_symbols(base_symbols, right_symbols))
    affected = sorted(
        set(intersection.shared_symbols)
        | (set(left_changed) & set(right_changed))
    )

    return {
        **record,
        "intersection": intersection.to_dict(),
        "affected_symbols": affected,
        "left_changed_symbols": left_changed,
        "right_changed_symbols": right_changed,
        "symbol_graph_base": build_graph(base_symbols).to_dict(),
        "symbol_graph_left": build_graph(left_symbols).to_dict(),
        "symbol_graph_right": build_graph(right_symbols).to_dict(),
    }


def detect_all(*, resume: bool = True) -> dict[str, int]:
    filtered = read_jsonl(FILTERED_JSONL)
    existing = load_existing_ids(CANDIDATES_JSONL) if resume else set()
    kept = 0
    stats = {"scanned": 0, "kept": 0}

    for record in progress(filtered, desc="detect candidates", total=len(filtered)):
        stats["scanned"] += 1
        if record["id"] in existing:
            continue
        candidate = analyze_candidate(record)
        if candidate is None:
            continue
        append_jsonl(CANDIDATES_JSONL, candidate)
        existing.add(record["id"])
        kept += 1
        stats["kept"] = kept

    logger.info("Candidate detection: scanned=%d kept=%d", stats["scanned"], stats["kept"])
    return stats
