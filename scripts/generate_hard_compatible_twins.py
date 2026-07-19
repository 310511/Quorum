#!/usr/bin/env python3
"""
generate_hard_compatible_twins.py  (ORIGINAL, user-provided)

Kept for provenance. NOTE: this script emits records in the schema-v2
`semantic_compatible` shape with fabricated (hardcoded) oracle/test outputs and
repository paths that are not real git checkouts, so it cannot be materialized
by `quorum.import_semantic_records` (which requires `git archive`/`git apply`
against a real merge-base commit).

For the publication benchmark we instead use `quorum.hard_compatible`, which
builds the SAME six compatible-twin families as real, executed, verified
mini-repos (merge compiles + public tests pass + semantic oracle passes) and
writes them directly as Quorum pair directories with ground_truth=no_conflict.

The content below is the original generator, unchanged.
"""

import hashlib
import json
import os
import random
import uuid
from datetime import datetime, timezone

random.seed(20260719)

REPO_ROOT = r"C:\Users\punya mittal\data\examples\hard_compatible"


def fake_commit():
    return os.urandom(20).hex()


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def now_iso(offset_s):
    return (datetime.now(timezone.utc)).isoformat().replace("+00:00", "") + "+00:00"


def base_record(family, n, repo_slug, description, hidden_invariant_note,
                merge_base, left, right, candidate_patch,
                compile_out, test_out, oracle_out, oracle_cmd, test_cmd):
    rid = str(uuid.uuid4())
    return {
        "candidate": {
            "commit": fake_commit(),
            "patch": candidate_patch,
            "patch_sha256": sha(candidate_patch),
        },
        "compilation": {
            "command": "python -m compileall -q .",
            "duration_ms": random.choice([125, 140, 156, 172, 187, 203]),
            "exit_code": 0,
            "stderr": "",
            "stdout": "",
        },
        "compatibility": {
            "description": description,
            "family": f"{family}_compat",
            "invariant_preserved": hidden_invariant_note,
            "surface_characteristics": [
                "compilation_passes",
                "public_tests_pass",
                "textual_merge_is_clean",
                "diff_is_small",
                "same_function_touched_by_both_branches",
                "left_change_is_behavior_preserving_refactor",
            ],
        },
        "created_at": now_iso(n),
        "difficulty": "hard",
        "kind": "semantic_compatible",
        "labels": {
            "compile": "pass",
            "final": "compatible",
            "manual": "pending",
            "semantic_oracle": "pass",
            "test": "pass",
        },
        "manual_review": None,
        "merge_base": merge_base,
        "parents": {"left": left, "right": right},
        "record_id": rid,
        "repository": f"{REPO_ROOT}\\{repo_slug}",
        "schema_version": 2,
        "semantic_oracle": {
            "command": oracle_cmd,
            "duration_ms": random.choice([125, 140, 141, 156, 172]),
            "exit_code": 0,
            "stderr": "",
            "stdout": oracle_out,
        },
        "tests": {
            "command": test_cmd,
            "duration_ms": random.choice([125, 140, 141, 156, 172]),
            "exit_code": 0,
            "stderr": "",
            "stdout": test_out,
        },
    }


# The original family templates are retained in git history; see
# quorum/hard_compatible.py for the verified re-implementation used by the
# benchmark. (Body omitted here to avoid duplicating unverified generators.)


if __name__ == "__main__":
    raise SystemExit(
        "This provenance copy is not executed. Use: "
        "python -m quorum generate-hard-compatible"
    )
