"""Tests for publication statistics helpers."""

from __future__ import annotations

from quorum.publication import _wilson_ci, mcnemar_test


def test_wilson_ci_bounds_for_known_rate() -> None:
    lo, hi = _wilson_ci(9, 16)
    assert 0.0 <= lo <= 9 / 16 <= hi <= 1.0
    assert hi - lo < 0.5


def test_mcnemar_detects_discordant_pairs() -> None:
    truth = ["conflict"] * 10
    pred_a = ["conflict"] * 8 + ["no_conflict"] * 2
    pred_b = ["conflict"] * 5 + ["no_conflict"] * 5
    stats = mcnemar_test(pred_a, pred_b, truth)
    assert stats["n_discordant"] == 3
    assert stats["b10"] == 3  # A correct, B wrong on 3 cases
    assert stats["p_value"] < 1.0
