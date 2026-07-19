"""Verified generation of hard compatible twins (true negatives)."""

from __future__ import annotations

import json
from pathlib import Path

from quorum.hard_compatible import FAMILY_BUILDERS, generate_hard_compatible


def test_generates_one_verified_twin_per_family(tmp_path: Path) -> None:
    dest = tmp_path / "twins"
    names = generate_hard_compatible(dest, per_family=1)
    assert len(names) == len(FAMILY_BUILDERS)
    for name in names:
        pair = dest / name
        label = json.loads((pair / "label.json").read_text(encoding="utf-8"))
        assert label["ground_truth"] == "no_conflict"
        assert label["validation"]["semantic_oracle"] == "pass"
        assert label["validation"]["final"] == "compatible"
        # Both branches must touch the same module (surface mimics conflict twins).
        assert (pair / "branch_a.diff").read_text(encoding="utf-8").strip()
        assert (pair / "branch_b.diff").read_text(encoding="utf-8").strip()


def test_left_diff_is_behavior_preserving(tmp_path: Path) -> None:
    dest = tmp_path / "twins"
    generate_hard_compatible(dest, per_family=1)
    diff = (dest / "twin_boundary_contract_0001" / "branch_a.diff").read_text(
        encoding="utf-8"
    )
    # Left branch adds only a docstring; the comparison operator is untouched.
    assert '"""' in diff
    assert ">=" not in diff
