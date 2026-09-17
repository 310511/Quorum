"""Phase 7: build human review queue CSV."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

from real_world.common import read_jsonl
from real_world.config import HEURISTICS_JSONL, REVIEW_QUEUE_CSV

logger = logging.getLogger(__name__)

COLUMNS = (
    "id",
    "repository",
    "category",
    "estimated_label",
    "confidence",
    "files",
    "symbols",
    "reason",
)


def build_review_queue(
    *,
    source_jsonl: Path = HEURISTICS_JSONL,
    output_csv: Path = REVIEW_QUEUE_CSV,
    limit: int | None = None,
) -> int:
    records = read_jsonl(source_jsonl)
    records.sort(
        key=lambda r: (
            -float(r.get("heuristic", {}).get("confidence", 0)),
            r.get("repository", ""),
            r.get("id", ""),
        )
    )
    if limit:
        records = records[:limit]

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        for record in records:
            heuristic = record.get("heuristic", {})
            writer.writerow(
                {
                    "id": record["id"],
                    "repository": record["repository"],
                    "category": record.get("semantic_category", "Other"),
                    "estimated_label": heuristic.get("estimated_label", "uncertain"),
                    "confidence": f"{heuristic.get('confidence', 0):.3f}",
                    "files": ";".join(record.get("executable_python_files", [])[:10]),
                    "symbols": ";".join(record.get("affected_symbols", [])[:15]),
                    "reason": heuristic.get("reason", ""),
                }
            )

    logger.info("Review queue written: %s (%d rows)", output_csv, len(records))
    return len(records)
