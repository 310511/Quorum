"""Phase 9: inter-reviewer agreement analysis."""

from __future__ import annotations

import logging
from collections import Counter
from pathlib import Path
from typing import Any

from real_world.common import read_jsonl, write_json
from real_world.config import AGREEMENT_REPORT, REVIEWER_A_JSONL, REVIEWER_B_JSONL

logger = logging.getLogger(__name__)

VALID_LABELS = frozenset({"conflict", "compatible", "skip"})


def _labels_by_id(path: Path) -> dict[str, str]:
    labels: dict[str, str] = {}
    for row in read_jsonl(path):
        example_id = row.get("id") or row.get("example_id")
        label = row.get("label")
        if not example_id or label not in VALID_LABELS:
            continue
        labels[str(example_id)] = str(label)
    return labels


def cohens_kappa(rater_a: dict[str, str], rater_b: dict[str, str]) -> float:
    """Cohen's kappa for categorical labels on shared examples (skip excluded)."""
    ids = sorted(set(rater_a) & set(rater_b))
    pairs = [
        (rater_a[i], rater_b[i])
        for i in ids
        if rater_a[i] != "skip" and rater_b[i] != "skip"
    ]
    n = len(pairs)
    if n == 0:
        return 0.0

    agree = sum(1 for a, b in pairs if a == b)
    p_o = agree / n
    labels = sorted({label for a, b in pairs for label in (a, b)})
    p_e = 0.0
    for label in labels:
        p_a = sum(1 for a, _ in pairs if a == label) / n
        p_b = sum(1 for _, b in pairs if b == label) / n
        p_e += p_a * p_b
    if p_e == 1.0:
        return 1.0
    return (p_o - p_e) / (1 - p_e)


def build_agreement_report(
    reviewer_a: Path = REVIEWER_A_JSONL,
    reviewer_b: Path = REVIEWER_B_JSONL,
    output: Path = AGREEMENT_REPORT,
) -> dict[str, Any]:
    a = _labels_by_id(reviewer_a)
    b = _labels_by_id(reviewer_b)
    shared = sorted(set(a) & set(b))
    disagreements: list[dict[str, str]] = []
    agreements = 0
    decided = 0

    for example_id in shared:
        la, lb = a[example_id], b[example_id]
        if la == "skip" or lb == "skip":
            continue
        decided += 1
        if la == lb:
            agreements += 1
        else:
            disagreements.append({"id": example_id, "reviewer_a": la, "reviewer_b": lb})

    kappa = cohens_kappa(a, b)
    agreement_rate = agreements / decided if decided else 0.0

    report = {
        "shared_examples": len(shared),
        "decided_examples": decided,
        "agreements": agreements,
        "disagreements": len(disagreements),
        "agreement_rate": agreement_rate,
        "cohens_kappa": kappa,
        "disagreement_cases": disagreements,
        "label_distribution_a": dict(Counter(a.values())),
        "label_distribution_b": dict(Counter(b.values())),
    }

    lines = [
        "# Real-world dataset — reviewer agreement report",
        "",
        f"- Shared examples reviewed: **{len(shared)}**",
        f"- Decided (non-skip) examples: **{decided}**",
        f"- Agreements: **{agreements}**",
        f"- Disagreements: **{len(disagreements)}**",
        f"- Agreement rate: **{agreement_rate:.1%}**",
        f"- Cohen's κ: **{kappa:.3f}**",
        "",
        "## Disagreements",
        "",
    ]
    if disagreements:
        lines.append("| id | reviewer_A | reviewer_B |")
        lines.append("|---|---|---|")
        for row in disagreements:
            lines.append(f"| {row['id']} | {row['reviewer_a']} | {row['reviewer_b']} |")
    else:
        lines.append("_None_")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(output.with_suffix(".json"), report)
    logger.info("Agreement report written to %s", output)
    return report
