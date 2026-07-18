"""Validation and inventory helpers for Quorum JSONL datasets."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DatasetAudit:
    total_records: int = 0
    usable_baselines: int = 0
    usable_synthetic_records: int = 0
    usable_agent_records: int = 0
    candidate_agent_pairs: int = 0
    rejected_records: int = 0
    pending_manual_review: int = 0
    kinds: dict[str, int] = field(default_factory=dict)
    mutation_types: dict[str, int] = field(default_factory=dict)
    rejection_reasons: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_records": self.total_records,
            "usable": {
                "baselines": self.usable_baselines,
                "synthetic_single_patch": self.usable_synthetic_records,
                "agent_records": self.usable_agent_records,
                "candidate_agent_pairs": self.candidate_agent_pairs,
            },
            "rejected_records": self.rejected_records,
            "pending_manual_review": self.pending_manual_review,
            "kinds": self.kinds,
            "mutation_types": self.mutation_types,
            "rejection_reasons": self.rejection_reasons,
            "warnings": self.warnings,
        }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load records while reporting the exact line containing invalid JSON."""
    records: list[dict[str, Any]] = []
    with Path(path).open(encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: record must be a JSON object")
            records.append(value)
    return records


def audit_records(records: list[dict[str, Any]]) -> DatasetAudit:
    """Separate valid single-patch examples from real branch-pair candidates."""
    audit = DatasetAudit(total_records=len(records))
    kinds: Counter[str] = Counter()
    mutations: Counter[str] = Counter()
    rejection_reasons: Counter[str] = Counter()
    pair_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for record in records:
        kind = str(record.get("kind") or "unknown")
        kinds[kind] += 1
        labels = record.get("labels") or {}
        if labels.get("manual") == "pending":
            audit.pending_manual_review += 1

        patch = str((record.get("candidate") or {}).get("patch") or "")
        test_label = labels.get("test")
        final_label = labels.get("final")

        if kind == "baseline":
            if patch:
                rejection_reasons["baseline_has_patch"] += 1
            elif test_label != "pass":
                rejection_reasons["baseline_tests_failed"] += 1
            else:
                audit.usable_baselines += 1
            continue

        if kind == "synthetic_mutation":
            mutation = record.get("mutation") or {}
            mutation_name = str(mutation.get("name") or "unknown")
            mutations[mutation_name] += 1
            expected = mutation.get("expected_label")
            if not patch:
                rejection_reasons["empty_patch"] += 1
            elif expected and expected != final_label:
                rejection_reasons["expected_label_mismatch"] += 1
            elif final_label == "negative" and test_label != "fail":
                rejection_reasons["negative_but_tests_pass"] += 1
            else:
                audit.usable_synthetic_records += 1
            continue

        if kind == "agent_candidate":
            generator = record.get("generator") or {}
            if not patch:
                if generator.get("files_applied") == 0:
                    rejection_reasons["agent_applied_no_files"] += 1
                else:
                    rejection_reasons["empty_patch"] += 1
                continue
            if test_label != "pass":
                rejection_reasons["agent_tests_failed"] += 1
                continue
            audit.usable_agent_records += 1
            pair_id = record.get("pair_id")
            if pair_id:
                pair_groups[str(pair_id)].append(record)
            else:
                rejection_reasons["agent_missing_pair_id"] += 1
            continue

        rejection_reasons["unknown_kind"] += 1

    for group in pair_groups.values():
        repositories = {r.get("repository") for r in group}
        merge_bases = {r.get("merge_base") for r in group}
        patches = {
            (r.get("candidate") or {}).get("patch")
            for r in group
            if (r.get("candidate") or {}).get("patch")
        }
        if len(group) >= 2 and len(repositories) == 1 and len(merge_bases) == 1 and len(patches) >= 2:
            audit.candidate_agent_pairs += 1

    audit.kinds = dict(sorted(kinds.items()))
    audit.mutation_types = dict(sorted(mutations.items()))
    audit.rejection_reasons = dict(sorted(rejection_reasons.items()))
    audit.rejected_records = sum(rejection_reasons.values())
    audit.warnings = [
        "Synthetic mutations are useful single-patch validity examples, not "
        "semantic merge-conflict pairs.",
        "Agent records become Quorum evaluation pairs only after two non-empty "
        "branches share a merge base and the merged result is test/manual labeled.",
    ]
    return audit


def audit_dataset(path: Path) -> DatasetAudit:
    return audit_records(load_jsonl(path))
