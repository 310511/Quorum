"""Generate verified HARD COMPATIBLE twin pairs (true negatives).

Each twin mirrors a `hard_negatives` conflict family, but the left branch makes a
behavior-preserving refactor (docstring only) instead of a semantic change, while
the right branch adds new code that depends on the shared function's ORIGINAL
semantics. The merge is therefore genuinely safe:

  - Branch A alone: compiles, tests pass
  - Branch B alone: compiles, public tests pass, semantic oracle passes
  - Merged tree:    compiles, public tests pass, semantic oracle PASSES

This defeats naive "same function touched by both branches" / "diff size"
heuristics: surface characteristics match the conflict twins, but ground truth is
``no_conflict``. Every pair is validated by actually executing the code.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from quorum.hard_benchmark import _compile_ok, _diff_from_base, _tests_pass, _write_tree


@dataclass(frozen=True)
class TwinSpec:
    name: str
    family: str
    module: str
    base_src: str
    left_src: str  # behavior-preserving refactor of base_src (docstring only)
    right_added_src: str  # new dependent function(s)
    public_test_src: str
    oracle_src: str
    description: str
    invariant: str
    left_intent: str
    right_intent: str


def _dedent(text: str) -> str:
    return textwrap.dedent(text).lstrip("\n")


def _run_oracle(files: dict[str, str], timeout: float = 30.0) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix="quorum-twin-oracle-") as temp:
        work = Path(temp) / "repo"
        _write_tree(work, files)
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "oracle_semantic", "-v"],
            cwd=work,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result.returncode == 0, (result.stdout + "\n" + result.stderr).strip()


# ---------------------------------------------------------------------------
# Family builders. Each returns a TwinSpec for index n.
# ---------------------------------------------------------------------------

def _boundary_contract(n: int) -> TwinSpec:
    cutoff = 41 + 6 * (n - 1)
    module = f"policy_{n:03d}.py"
    base = _dedent(
        f"""
        def eligible_{n}(score, cutoff):
            return score > cutoff
        """
    )
    left = _dedent(
        f'''
        def eligible_{n}(score, cutoff):
            """Return True if score exceeds the cutoff."""
            return score > cutoff
        '''
    )
    right = _dedent(
        f"""
        def route_{n}(score):
            return "priority" if eligible_{n}(score, {cutoff}) else "standard"
        """
    )
    public = _dedent(
        f"""
        import unittest
        from policy_{n:03d} import route_{n}

        class PolicyTests(unittest.TestCase):
            def test_clear_priority(self):
                self.assertEqual(route_{n}({cutoff + 5}), "priority")
            def test_clear_standard(self):
                self.assertEqual(route_{n}({cutoff - 5}), "standard")

        if __name__ == "__main__":
            unittest.main()
        """
    )
    oracle = _dedent(
        f"""
        import unittest
        from policy_{n:03d} import route_{n}

        class SemanticOracle(unittest.TestCase):
            def test_boundary_remains_standard(self):
                self.assertEqual(route_{n}({cutoff}), "standard")
        """
    )
    return TwinSpec(
        name=f"twin_boundary_contract_{n:04d}",
        family="boundary_contract",
        module=module,
        base_src=base,
        left_src=left,
        right_added_src=right,
        public_test_src=public,
        oracle_src=oracle,
        description=(
            "Left adds a docstring only (comparison operator unchanged); right's "
            "new routing still sees strict '>' semantics, so a score exactly at "
            "the cutoff stays 'standard' after merge."
        ),
        invariant="A score exactly at the cutoff remains 'standard'.",
        left_intent="Document eligibility helper (no behavior change).",
        right_intent="Add routing that relies on the established strict threshold.",
    )


def _ordering_default(n: int) -> TwinSpec:
    a, b = 5 + 3 * n, 2 + 3 * n
    module = f"ordering_{n:03d}.py"
    base = _dedent(
        f"""
        def normalize_{n}(items, reverse=False):
            return sorted(items, reverse=reverse)
        """
    )
    left = _dedent(
        f'''
        def normalize_{n}(items, reverse=False):
            """Return items sorted according to `reverse`."""
            return sorted(items, reverse=reverse)
        '''
    )
    right = _dedent(
        f"""
        def first_{n}(items):
            return normalize_{n}(items)[0]
        """
    )
    public = _dedent(
        f"""
        import unittest
        from ordering_{n:03d} import first_{n}, normalize_{n}

        class OrderingTests(unittest.TestCase):
            def test_single_item(self):
                self.assertEqual(first_{n}([{b}]), {b})
            def test_equal_items(self):
                self.assertEqual(normalize_{n}([{b}, {b}]), [{b}, {b}])

        if __name__ == "__main__":
            unittest.main()
        """
    )
    oracle = _dedent(
        f"""
        import unittest
        from ordering_{n:03d} import first_{n}

        class SemanticOracle(unittest.TestCase):
            def test_first_means_smallest(self):
                self.assertEqual(first_{n}([{a}, {b}]), {b})
        """
    )
    return TwinSpec(
        name=f"twin_ordering_default_{n:04d}",
        family="ordering_default",
        module=module,
        base_src=base,
        left_src=left,
        right_added_src=right,
        public_test_src=public,
        oracle_src=oracle,
        description=(
            "Left adds a docstring only (default reverse=False unchanged); right's "
            "helper still sees ascending order, so 'first' stays the smallest item."
        ),
        invariant="first(items) still returns the smallest item.",
        left_intent="Document sort helper (default order unchanged).",
        right_intent="Add a helper that treats the default first item as the minimum.",
    )


def _sentinel_default(n: int) -> TwinSpec:
    default_val = 83 + 6 * n
    module = f"limits_{n:03d}.py"
    base = _dedent(
        f"""
        def resolve_limit_{n}(value):
            return {default_val} if value is None else value
        """
    )
    left = _dedent(
        f'''
        def resolve_limit_{n}(value):
            """Resolve a limit, defaulting when unset."""
            return {default_val} if value is None else value
        '''
    )
    right = _dedent(
        f"""
        def can_accept_{n}(current, limit=None):
            return current < resolve_limit_{n}(limit)
        """
    )
    public = _dedent(
        f"""
        import unittest
        from limits_{n:03d} import can_accept_{n}

        class LimitTests(unittest.TestCase):
            def test_explicit_limit(self):
                self.assertTrue(can_accept_{n}(4, 10))
                self.assertFalse(can_accept_{n}(10, 10))

        if __name__ == "__main__":
            unittest.main()
        """
    )
    oracle = _dedent(
        f"""
        import unittest
        from limits_{n:03d} import can_accept_{n}

        class SemanticOracle(unittest.TestCase):
            def test_missing_limit_uses_configured_default(self):
                self.assertTrue(can_accept_{n}(1))
        """
    )
    return TwinSpec(
        name=f"twin_sentinel_default_{n:04d}",
        family="sentinel_default",
        module=module,
        base_src=base,
        left_src=left,
        right_added_src=right,
        public_test_src=public,
        oracle_src=oracle,
        description=(
            f"Left adds a docstring only (default stays {default_val}); right's "
            "admission check still resolves a missing limit to the original default."
        ),
        invariant="An omitted limit still resolves to the original non-zero default.",
        left_intent="Document limit resolution (default value unchanged).",
        right_intent="Add admission logic relying on the configured missing-value default.",
    )


def _aliasing_contract(n: int) -> TwinSpec:
    a, b, c = 6 * n + 1, 6 * n + 2, 6 * n + 3
    module = f"records_{n:03d}.py"
    base = _dedent(
        f"""
        def select_{n}(values):
            return list(values)
        """
    )
    left = _dedent(
        f'''
        def select_{n}(values):
            """Return a copy of values."""
            return list(values)
        '''
    )
    right = _dedent(
        f"""
        def without_last_{n}(values):
            selected = select_{n}(values)
            if selected:
                selected.pop()
            return selected
        """
    )
    public = _dedent(
        f"""
        import unittest
        from records_{n:03d} import without_last_{n}

        class RecordTests(unittest.TestCase):
            def test_result_drops_last(self):
                self.assertEqual(without_last_{n}([{a}, {b}, {c}]), [{a}, {b}])

        if __name__ == "__main__":
            unittest.main()
        """
    )
    oracle = _dedent(
        f"""
        import unittest
        from records_{n:03d} import without_last_{n}

        class SemanticOracle(unittest.TestCase):
            def test_input_is_not_mutated(self):
                values = [{a}, {b}, {c}]
                without_last_{n}(values)
                self.assertEqual(values, [{a}, {b}, {c}])
        """
    )
    return TwinSpec(
        name=f"twin_aliasing_contract_{n:04d}",
        family="aliasing_contract",
        module=module,
        base_src=base,
        left_src=left,
        right_added_src=right,
        public_test_src=public,
        oracle_src=oracle,
        description=(
            "Left adds a docstring only (select still returns list(values), a real "
            "copy); right's mutation of the returned list never touches caller input."
        ),
        invariant="Read-style helpers never mutate caller-owned input.",
        left_intent="Document selection helper (still returns a copy).",
        right_intent="Add a convenience helper that edits its selected working set.",
    )


def _error_contract(n: int) -> TwinSpec:
    invalid_tag = 6 * n
    valid_num = 10 * n
    module = f"parser_{n:03d}.py"
    base = _dedent(
        f"""
        def parse_count_{n}(raw):
            return int(raw)
        """
    )
    left = _dedent(
        f'''
        def parse_count_{n}(raw):
            """Parse a count, raising ValueError for invalid input."""
            return int(raw)
        '''
    )
    right = _dedent(
        f"""
        def valid_count_{n}(raw):
            try:
                parse_count_{n}(raw)
                return True
            except ValueError:
                return False
        """
    )
    public = _dedent(
        f"""
        import unittest
        from parser_{n:03d} import parse_count_{n}, valid_count_{n}

        class ParserTests(unittest.TestCase):
            def test_valid_number(self):
                self.assertEqual(parse_count_{n}("{valid_num}"), {valid_num})
                self.assertTrue(valid_count_{n}("{valid_num}"))

        if __name__ == "__main__":
            unittest.main()
        """
    )
    oracle = _dedent(
        f"""
        import unittest
        from parser_{n:03d} import valid_count_{n}

        class SemanticOracle(unittest.TestCase):
            def test_invalid_number_is_rejected(self):
                self.assertFalse(valid_count_{n}("not-a-number-{invalid_tag}"))
        """
    )
    return TwinSpec(
        name=f"twin_error_contract_{n:04d}",
        family="error_contract",
        module=module,
        base_src=base,
        left_src=left,
        right_added_src=right,
        public_test_src=public,
        oracle_src=oracle,
        description=(
            "Left adds a docstring only (parse still raises ValueError, no silent "
            "fallback); right's validator still catches it, so invalid input is "
            "still rejected after merge."
        ),
        invariant="Non-numeric input is still reported as invalid.",
        left_intent="Document parsing helper (still raises ValueError on bad input).",
        right_intent="Add validation that detects invalid input via parse failures.",
    )


def _case_sensitivity(n: int) -> TwinSpec:
    tag = 6 * n
    module = f"identity_{n:03d}.py"
    base = _dedent(
        f"""
        def same_code_{n}(left, right):
            return left == right
        """
    )
    left = _dedent(
        f'''
        def same_code_{n}(left, right):
            """Return True if left equals right exactly (case-sensitive)."""
            return left == right
        '''
    )
    right = _dedent(
        f"""
        def authorized_{n}(presented, required):
            return same_code_{n}(presented, required)
        """
    )
    public = _dedent(
        f"""
        import unittest
        from identity_{n:03d} import authorized_{n}

        class IdentityTests(unittest.TestCase):
            def test_exact_identity(self):
                self.assertTrue(authorized_{n}("Admin{tag}", "Admin{tag}"))
            def test_different_identity(self):
                self.assertFalse(authorized_{n}("User{tag}", "Admin{tag}"))

        if __name__ == "__main__":
            unittest.main()
        """
    )
    oracle = _dedent(
        f"""
        import unittest
        from identity_{n:03d} import authorized_{n}

        class SemanticOracle(unittest.TestCase):
            def test_security_codes_remain_case_sensitive(self):
                self.assertFalse(authorized_{n}("admin{tag}", "Admin{tag}"))
        """
    )
    return TwinSpec(
        name=f"twin_case_sensitivity_{n:04d}",
        family="case_sensitivity",
        module=module,
        base_src=base,
        left_src=left,
        right_added_src=right,
        public_test_src=public,
        oracle_src=oracle,
        description=(
            "Left adds a docstring only (same_code still uses strict '=='); right's "
            "authorization check stays case-sensitive after merge."
        ),
        invariant="Authorization codes remain case-sensitive.",
        left_intent="Document identity comparison (still case-sensitive).",
        right_intent="Reuse identifier comparison for an authorization check.",
    )


FAMILY_BUILDERS: list[Callable[[int], TwinSpec]] = [
    _boundary_contract,
    _ordering_default,
    _sentinel_default,
    _aliasing_contract,
    _case_sensitivity,
    _error_contract,
]


def _materialize(spec: TwinSpec, destination: Path) -> bool:
    base = {spec.module: spec.base_src}
    left_overlay = {spec.module: spec.left_src}
    right_module = spec.base_src.rstrip() + "\n\n\n" + spec.right_added_src
    right_overlay = {
        spec.module: right_module,
        "test_public.py": spec.public_test_src,
        "oracle_semantic.py": spec.oracle_src,
    }
    merged_module = spec.left_src.rstrip() + "\n\n\n" + spec.right_added_src
    merged = {
        spec.module: merged_module,
        "test_public.py": spec.public_test_src,
        "oracle_semantic.py": spec.oracle_src,
    }
    tree_a = {**base, **left_overlay}
    tree_b = {**base, **right_overlay}

    if not (
        _compile_ok(tree_a)
        and _compile_ok(tree_b)
        and _compile_ok(merged)
    ):
        return False

    # Branch A alone: no public tests present -> discovery is trivially OK.
    a_ok, _ = _tests_pass(tree_a)
    b_pub_ok, _ = _tests_pass(tree_b)
    b_oracle_ok, _ = _run_oracle(tree_b)
    merged_pub_ok, merged_pub_out = _tests_pass(merged)
    merged_oracle_ok, merged_oracle_out = _run_oracle(merged)

    # A true compatible twin: everything passes, including the merged oracle.
    if not (a_ok and b_pub_ok and b_oracle_ok and merged_pub_ok and merged_oracle_ok):
        return False

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    _write_tree(destination / "merge_base", base)
    _write_tree(destination / "branch_a", left_overlay)
    _write_tree(destination / "branch_a_full", tree_a)
    _write_tree(destination / "branch_b", right_overlay)
    _write_tree(destination / "branch_b_full", tree_b)
    _write_tree(destination / "merged_full", merged)
    (destination / "branch_a.diff").write_text(
        _diff_from_base(base, left_overlay), encoding="utf-8"
    )
    (destination / "branch_b.diff").write_text(
        _diff_from_base(base, right_overlay), encoding="utf-8"
    )
    (destination / "context.md").write_text(
        "# Hard compatible twin (verified true negative)\n\n"
        f"- Family: `{spec.family}`\n"
        f"- Description: {spec.description}\n"
        f"- Preserved invariant: {spec.invariant}\n"
        f"- Left intent: {spec.left_intent}\n"
        f"- Right intent: {spec.right_intent}\n"
        "- Validation: branch A tests pass, branch B tests + oracle pass, "
        "merged tests + semantic oracle PASS (merge is safe).\n",
        encoding="utf-8",
    )
    label = {
        "ground_truth": "no_conflict",
        "language": "python",
        "source": "hard_compatible_twin_verified",
        "conflict_type": spec.family,
        "difficulty": "hard",
        "notes": spec.description,
        "hidden_invariant": spec.invariant,
        "surface_characteristics": [
            "compilation_passes",
            "public_tests_pass",
            "textual_merge_is_clean",
            "diff_is_small",
            "same_function_touched_by_both_branches",
            "left_change_is_behavior_preserving_refactor",
        ],
        "validation": {
            "compile": "pass",
            "public_tests": "pass",
            "semantic_oracle": "pass",
            "final": "compatible",
            "oracle_command": "python -m unittest oracle_semantic",
            "oracle_exit_code": 0,
            "merged_test_output": merged_pub_out[-1000:],
            "merged_oracle_output": merged_oracle_out[-1000:],
        },
    }
    (destination / "label.json").write_text(
        json.dumps(label, indent=2) + "\n", encoding="utf-8"
    )
    (destination / "meta.json").write_text(
        json.dumps(
            {
                "pair": spec.name,
                "family": spec.family,
                "ground_truth": "no_conflict",
                "generator": "quorum.hard_compatible",
                "twin_of_family": spec.family,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return True


def generate_hard_compatible(
    destination: Path,
    *,
    per_family: int = 17,
) -> list[str]:
    """Generate verified compatible twins (per_family per each of 6 families)."""
    destination.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    for builder in FAMILY_BUILDERS:
        for n in range(1, per_family + 1):
            spec = builder(n)
            if _materialize(spec, destination / spec.name):
                created.append(spec.name)
    return created
