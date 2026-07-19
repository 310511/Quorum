"""Generate verified hard semantic-conflict mini-repos for publication benchmarks.

Each example is a self-contained Python project where:
  - Branch A alone: compiles and all tests pass
  - Branch B alone: compiles and all tests pass
  - Merged tree: compiles but tests fail (semantic inconsistency)

Compatible controls (orthogonal edits) are also generated for class balance.
"""

from __future__ import annotations

import difflib
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class HardPairSpec:
    name: str
    conflict_type: str
    ground_truth: str  # conflict | no_conflict
    merge_base: dict[str, str]
    branch_a: dict[str, str]
    branch_b: dict[str, str]
    notes: str


def _unified_diff(rel: str, before: str | None, after: str) -> str:
    original = (before or "").splitlines(keepends=True)
    updated = after.splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(original, updated, fromfile=f"a/{rel}", tofile=f"b/{rel}")
    )


def _diff_from_base(base: dict[str, str], overlay: dict[str, str]) -> str:
    chunks: list[str] = []
    for rel, content in sorted(overlay.items()):
        chunk = _unified_diff(rel, base.get(rel), content)
        if chunk.strip():
            chunks.append(chunk.rstrip())
    return "\n".join(chunks)


def _write_tree(root: Path, files: dict[str, str]) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")


def _compile_ok(files: dict[str, str]) -> bool:
    with tempfile.TemporaryDirectory(prefix="quorum-compile-") as temp:
        work = Path(temp)
        for rel, content in files.items():
            path = work / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")
        for path in work.rglob("*.py"):
            source = path.read_text(encoding="utf-8")
            try:
                compile(source, str(path), "exec")
            except SyntaxError:
                return False
        return True


def _tests_pass(files: dict[str, str], timeout: float = 30.0) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix="quorum-hard-") as temp:
        work = Path(temp) / "repo"
        _write_tree(work, files)
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-v"],
            cwd=work,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        output = (result.stdout + "\n" + result.stderr).strip()
        return result.returncode == 0, output


def _merge(base: dict[str, str], a: dict[str, str], b: dict[str, str]) -> dict[str, str]:
    return {**base, **a, **b}


# ---------------------------------------------------------------------------
# Conflict templates. Each builder returns a HardPairSpec for index i.
# ---------------------------------------------------------------------------

DOMAINS = [
    "billing",
    "shipping",
    "inventory",
    "auth",
    "cache",
    "metrics",
    "parser",
    "scheduler",
    "notifier",
    "ledger",
    "catalog",
    "routing",
    "pricing",
    "analytics",
    "checkout",
    "warehouse",
    "tickets",
    "payments",
    "search",
    "profile",
]


def _rename_stale(i: int, domain: str) -> HardPairSpec:
    symbol = f"compute_{domain}_total"
    renamed = f"{symbol}_v2"
    base = {
        f"{domain}_core.py": f"""
            def {symbol}(items):
                return sum(int(x) for x in items)

            def format_total(items):
                return "total=" + str({symbol}(items))
            """,
        f"test_{domain}_core.py": f"""
            import unittest
            from {domain}_core import {symbol}, format_total

            class CoreTests(unittest.TestCase):
                def test_total(self):
                    self.assertEqual({symbol}([1, 2, 3]), 6)
                def test_format(self):
                    self.assertIn("6", format_total([1, 2, 3]))

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    branch_a = {
        f"{domain}_core.py": f"""
            def {renamed}(items):
                return sum(int(x) for x in items)

            def format_total(items):
                return "total=" + str({renamed}(items))
            """,
        f"test_{domain}_core.py": f"""
            import unittest
            from {domain}_core import {renamed}, format_total

            class CoreTests(unittest.TestCase):
                def test_total(self):
                    self.assertEqual({renamed}([1, 2, 3]), 6)
                def test_format(self):
                    self.assertIn("6", format_total([1, 2, 3]))

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    branch_b = {
        f"{domain}_report.py": f"""
            from {domain}_core import {symbol}

            def report_line(items):
                return {symbol}(items) * 2
            """,
        f"test_{domain}_report.py": f"""
            import unittest
            from {domain}_report import report_line

            class ReportTests(unittest.TestCase):
                def test_report(self):
                    self.assertEqual(report_line([1, 2, 3]), 12)

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    return HardPairSpec(
        name=f"hard_{i:03d}_{domain}_rename_stale",
        conflict_type="rename_stale_reference",
        ground_truth="conflict",
        merge_base=base,
        branch_a=branch_a,
        branch_b=branch_b,
        notes=f"Branch A renames {symbol}->{renamed}; Branch B adds caller of {symbol}",
    )


def _signature_break(i: int, domain: str) -> HardPairSpec:
    base = {
        f"{domain}_api.py": f"""
            def build_{domain}_payload(name, quantity=1):
                return {{"name": name, "quantity": quantity, "kind": "{domain}"}}

            def summarize(name):
                return build_{domain}_payload(name)["quantity"]
            """,
        f"test_{domain}_api.py": f"""
            import unittest
            from {domain}_api import build_{domain}_payload, summarize

            class ApiTests(unittest.TestCase):
                def test_payload(self):
                    self.assertEqual(build_{domain}_payload("x")["quantity"], 1)
                def test_summarize(self):
                    self.assertEqual(summarize("x"), 1)

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    branch_a = {
        f"{domain}_api.py": f"""
            def build_{domain}_payload(name, *, quantity, priority):
                return {{
                    "name": name,
                    "quantity": quantity,
                    "priority": priority,
                    "kind": "{domain}",
                }}

            def summarize(name):
                return build_{domain}_payload(name, quantity=1, priority="normal")["quantity"]
            """,
        f"test_{domain}_api.py": f"""
            import unittest
            from {domain}_api import build_{domain}_payload, summarize

            class ApiTests(unittest.TestCase):
                def test_payload(self):
                    payload = build_{domain}_payload("x", quantity=2, priority="high")
                    self.assertEqual(payload["quantity"], 2)
                    self.assertEqual(payload["priority"], "high")
                def test_summarize(self):
                    self.assertEqual(summarize("x"), 1)

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    branch_b = {
        f"{domain}_client.py": f"""
            from {domain}_api import build_{domain}_payload

            def client_order(name):
                # Relies on old positional/default signature.
                return build_{domain}_payload(name, 5)
            """,
        f"test_{domain}_client.py": f"""
            import unittest
            from {domain}_client import client_order

            class ClientTests(unittest.TestCase):
                def test_order(self):
                    self.assertEqual(client_order("sku")["quantity"], 5)

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    return HardPairSpec(
        name=f"hard_{i:03d}_{domain}_signature_break",
        conflict_type="signature_break",
        ground_truth="conflict",
        merge_base=base,
        branch_a=branch_a,
        branch_b=branch_b,
        notes="Branch A makes quantity/priority keyword-only; Branch B still calls positionally",
    )


def _import_drift(i: int, domain: str) -> HardPairSpec:
    base = {
        f"{domain}_utils.py": f"""
            def normalize_{domain}_token(value):
                return str(value).strip().lower()
            """,
        f"test_{domain}_utils.py": f"""
            import unittest
            from {domain}_utils import normalize_{domain}_token

            class UtilsTests(unittest.TestCase):
                def test_normalize(self):
                    self.assertEqual(normalize_{domain}_token(" Ab "), "ab")

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    branch_a = {
        f"{domain}_tokens.py": f"""
            def normalize_{domain}_token(value):
                return str(value).strip().lower()
            """,
        # Remove old module by emptying/replacing with re-export failure path:
        # delete by writing a stub that does not export the symbol.
        f"{domain}_utils.py": f"""
            # Moved to {domain}_tokens.py
            """,
        f"test_{domain}_utils.py": f"""
            import unittest
            from {domain}_tokens import normalize_{domain}_token

            class UtilsTests(unittest.TestCase):
                def test_normalize(self):
                    self.assertEqual(normalize_{domain}_token(" Ab "), "ab")

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    branch_b = {
        f"{domain}_pipeline.py": f"""
            from {domain}_utils import normalize_{domain}_token

            def pipeline_key(value):
                return "key:" + normalize_{domain}_token(value)
            """,
        f"test_{domain}_pipeline.py": f"""
            import unittest
            from {domain}_pipeline import pipeline_key

            class PipelineTests(unittest.TestCase):
                def test_key(self):
                    self.assertEqual(pipeline_key(" X "), "key:x")

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    return HardPairSpec(
        name=f"hard_{i:03d}_{domain}_import_drift",
        conflict_type="import_drift",
        ground_truth="conflict",
        merge_base=base,
        branch_a=branch_a,
        branch_b=branch_b,
        notes=f"Branch A moves normalize_{domain}_token; Branch B still imports {domain}_utils",
    )


def _return_contract(i: int, domain: str) -> HardPairSpec:
    base = {
        f"{domain}_service.py": f"""
            def fetch_{domain}_record(item_id):
                return {{"id": item_id, "status": "ok", "score": 1}}

            def status_of(item_id):
                return fetch_{domain}_record(item_id)["status"]
            """,
        f"test_{domain}_service.py": f"""
            import unittest
            from {domain}_service import fetch_{domain}_record, status_of

            class ServiceTests(unittest.TestCase):
                def test_record(self):
                    self.assertEqual(fetch_{domain}_record(7)["score"], 1)
                def test_status(self):
                    self.assertEqual(status_of(7), "ok")

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    branch_a = {
        f"{domain}_service.py": f"""
            def fetch_{domain}_record(item_id):
                # New contract: nested payload, no top-level score.
                return {{"id": item_id, "status": "ok", "meta": {{"score": 1}}}}

            def status_of(item_id):
                return fetch_{domain}_record(item_id)["status"]
            """,
        f"test_{domain}_service.py": f"""
            import unittest
            from {domain}_service import fetch_{domain}_record, status_of

            class ServiceTests(unittest.TestCase):
                def test_record(self):
                    self.assertEqual(fetch_{domain}_record(7)["meta"]["score"], 1)
                def test_status(self):
                    self.assertEqual(status_of(7), "ok")

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    branch_b = {
        f"{domain}_scorecard.py": f"""
            from {domain}_service import fetch_{domain}_record

            def score_for(item_id):
                return fetch_{domain}_record(item_id)["score"] + 10
            """,
        f"test_{domain}_scorecard.py": f"""
            import unittest
            from {domain}_scorecard import score_for

            class ScorecardTests(unittest.TestCase):
                def test_score(self):
                    self.assertEqual(score_for(3), 11)

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    return HardPairSpec(
        name=f"hard_{i:03d}_{domain}_return_contract",
        conflict_type="return_contract",
        ground_truth="conflict",
        merge_base=base,
        branch_a=branch_a,
        branch_b=branch_b,
        notes="Branch A nests score under meta; Branch B still reads top-level score",
    )


def _exception_contract(i: int, domain: str) -> HardPairSpec:
    base = {
        f"{domain}_guard.py": f"""
            class {domain.title()}Error(ValueError):
                pass

            def ensure_{domain}_positive(value):
                if value <= 0:
                    raise {domain.title()}Error("non-positive")
                return value
            """,
        f"test_{domain}_guard.py": f"""
            import unittest
            from {domain}_guard import ensure_{domain}_positive, {domain.title()}Error

            class GuardTests(unittest.TestCase):
                def test_ok(self):
                    self.assertEqual(ensure_{domain}_positive(2), 2)
                def test_bad(self):
                    with self.assertRaises({domain.title()}Error):
                        ensure_{domain}_positive(0)

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    branch_a = {
        f"{domain}_guard.py": f"""
            class {domain.title()}Gone(LookupError):
                pass

            def ensure_{domain}_positive(value):
                if value <= 0:
                    raise {domain.title()}Gone("non-positive")
                return value
            """,
        f"test_{domain}_guard.py": f"""
            import unittest
            from {domain}_guard import ensure_{domain}_positive, {domain.title()}Gone

            class GuardTests(unittest.TestCase):
                def test_ok(self):
                    self.assertEqual(ensure_{domain}_positive(2), 2)
                def test_bad(self):
                    with self.assertRaises({domain.title()}Gone):
                        ensure_{domain}_positive(0)

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    branch_b = {
        f"{domain}_handler.py": f"""
            from {domain}_guard import ensure_{domain}_positive, {domain.title()}Error

            def safe_{domain}(value):
                try:
                    return ensure_{domain}_positive(value)
                except {domain.title()}Error:
                    return 0
            """,
        f"test_{domain}_handler.py": f"""
            import unittest
            from {domain}_handler import safe_{domain}

            class HandlerTests(unittest.TestCase):
                def test_safe(self):
                    self.assertEqual(safe_{domain}(0), 0)
                    self.assertEqual(safe_{domain}(4), 4)

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    return HardPairSpec(
        name=f"hard_{i:03d}_{domain}_exception_contract",
        conflict_type="exception_contract",
        ground_truth="conflict",
        merge_base=base,
        branch_a=branch_a,
        branch_b=branch_b,
        notes="Branch A changes exception type; Branch B still catches the old type",
    )


def _default_semantics(i: int, domain: str) -> HardPairSpec:
    base = {
        f"{domain}_config.py": f"""
            DEFAULT_LIMIT = 10

            def page_{domain}(items, limit=DEFAULT_LIMIT):
                return list(items)[:limit]
            """,
        f"test_{domain}_config.py": f"""
            import unittest
            from {domain}_config import page_{domain}

            class ConfigTests(unittest.TestCase):
                def test_page(self):
                    self.assertEqual(page_{domain}(range(20)), list(range(10)))

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    branch_a = {
        f"{domain}_config.py": f"""
            DEFAULT_LIMIT = 3

            def page_{domain}(items, limit=DEFAULT_LIMIT):
                return list(items)[:limit]
            """,
        f"test_{domain}_config.py": f"""
            import unittest
            from {domain}_config import page_{domain}

            class ConfigTests(unittest.TestCase):
                def test_page(self):
                    self.assertEqual(page_{domain}(range(20)), list(range(3)))

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    branch_b = {
        f"{domain}_ui.py": f"""
            from {domain}_config import page_{domain}

            def preview_{domain}():
                # Depends on historical default of 10.
                return page_{domain}(range(20))
            """,
        f"test_{domain}_ui.py": f"""
            import unittest
            from {domain}_ui import preview_{domain}

            class UiTests(unittest.TestCase):
                def test_preview(self):
                    self.assertEqual(len(preview_{domain}()), 10)

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    return HardPairSpec(
        name=f"hard_{i:03d}_{domain}_default_semantics",
        conflict_type="default_semantics",
        ground_truth="conflict",
        merge_base=base,
        branch_a=branch_a,
        branch_b=branch_b,
        notes="Branch A changes DEFAULT_LIMIT 10->3; Branch B asserts old default length",
    )


def _compatible_orthogonal(i: int, domain: str) -> HardPairSpec:
    """Negative control: two non-overlapping, compatible feature additions."""
    base = {
        f"{domain}_base.py": f"""
            def identity_{domain}(value):
                return value
            """,
        f"test_{domain}_base.py": f"""
            import unittest
            from {domain}_base import identity_{domain}

            class BaseTests(unittest.TestCase):
                def test_identity(self):
                    self.assertEqual(identity_{domain}(5), 5)

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    branch_a = {
        f"{domain}_alpha.py": f"""
            def alpha_{domain}(value):
                return value + 1
            """,
        f"test_{domain}_alpha.py": f"""
            import unittest
            from {domain}_alpha import alpha_{domain}

            class AlphaTests(unittest.TestCase):
                def test_alpha(self):
                    self.assertEqual(alpha_{domain}(1), 2)

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    branch_b = {
        f"{domain}_beta.py": f"""
            def beta_{domain}(value):
                return value * 2
            """,
        f"test_{domain}_beta.py": f"""
            import unittest
            from {domain}_beta import beta_{domain}

            class BetaTests(unittest.TestCase):
                def test_beta(self):
                    self.assertEqual(beta_{domain}(3), 6)

            if __name__ == "__main__":
                unittest.main()
            """,
    }
    return HardPairSpec(
        name=f"hard_{i:03d}_{domain}_compatible",
        conflict_type="orthogonal_features",
        ground_truth="no_conflict",
        merge_base=base,
        branch_a=branch_a,
        branch_b=branch_b,
        notes="Independent new modules; merge should remain compatible",
    )


CONFLICT_BUILDERS: list[Callable[[int, str], HardPairSpec]] = [
    _rename_stale,
    _signature_break,
    _import_drift,
    _return_contract,
    _exception_contract,
    _default_semantics,
]


def _materialize(spec: HardPairSpec, destination: Path) -> bool:
    """Validate and write a pair. Returns True on success."""
    base = {k: textwrap.dedent(v).lstrip("\n") for k, v in spec.merge_base.items()}
    a_overlay = {k: textwrap.dedent(v).lstrip("\n") for k, v in spec.branch_a.items()}
    b_overlay = {k: textwrap.dedent(v).lstrip("\n") for k, v in spec.branch_b.items()}
    tree_a = {**base, **a_overlay}
    tree_b = {**base, **b_overlay}
    tree_m = _merge(base, a_overlay, b_overlay)

    if not (_compile_ok(tree_a) and _compile_ok(tree_b) and _compile_ok(tree_m)):
        return False

    a_ok, _ = _tests_pass(tree_a)
    b_ok, _ = _tests_pass(tree_b)
    m_ok, m_out = _tests_pass(tree_m)
    if not a_ok or not b_ok:
        return False
    if spec.ground_truth == "conflict" and m_ok:
        return False
    if spec.ground_truth == "no_conflict" and not m_ok:
        return False

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    _write_tree(destination / "merge_base", base)
    _write_tree(destination / "branch_a", a_overlay)
    # branch snapshots for inspection also include base overlay for readability
    _write_tree(destination / "branch_a_full", tree_a)
    _write_tree(destination / "branch_b", b_overlay)
    _write_tree(destination / "branch_b_full", tree_b)
    (destination / "branch_a.diff").write_text(
        _diff_from_base(base, a_overlay), encoding="utf-8"
    )
    (destination / "branch_b.diff").write_text(
        _diff_from_base(base, b_overlay), encoding="utf-8"
    )
    (destination / "context.md").write_text(
        "# Hard semantic benchmark pair\n\n"
        f"- Conflict type: `{spec.conflict_type}`\n"
        f"- Ground truth: `{spec.ground_truth}`\n"
        f"- Notes: {spec.notes}\n"
        "- Validation: Branch A tests pass, Branch B tests pass, "
        + (
            "merged tests fail (semantic conflict).\n"
            if spec.ground_truth == "conflict"
            else "merged tests pass (compatible).\n"
        ),
        encoding="utf-8",
    )
    label = {
        "ground_truth": spec.ground_truth,
        "language": "python",
        "source": "hard_benchmark_verified",
        "conflict_type": spec.conflict_type,
        "notes": spec.notes,
        "validation": {
            "branch_a_tests": "pass",
            "branch_b_tests": "pass",
            "merged_tests": "fail" if spec.ground_truth == "conflict" else "pass",
            "compilation": "pass",
            "merged_test_output": m_out[-2000:],
        },
    }
    (destination / "label.json").write_text(
        json.dumps(label, indent=2) + "\n", encoding="utf-8"
    )
    (destination / "meta.json").write_text(
        json.dumps(
            {
                "pair": spec.name,
                "conflict_type": spec.conflict_type,
                "ground_truth": spec.ground_truth,
                "generator": "quorum.hard_benchmark",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return True


def generate_hard_benchmark(
    destination: Path,
    *,
    n_conflicts: int = 100,
    n_compatible: int = 30,
    seed: int = 42,
) -> list[str]:
    """Generate verified hard pairs. Returns list of created pair names."""
    rng = random.Random(seed)
    destination.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    domains = list(DOMAINS)
    rng.shuffle(domains)

    # Conflicts: cycle builders × domains until quota filled.
    index = 0
    attempts = 0
    while len([c for c in created if "_compatible" not in c]) < n_conflicts and attempts < n_conflicts * 5:
        attempts += 1
        domain = domains[index % len(domains)]
        # uniquify domain when recycling
        domain_use = domain if index < len(domains) else f"{domain}_{index // len(domains)}"
        domain_use = re.sub(r"[^a-z0-9_]", "_", domain_use)
        builder = CONFLICT_BUILDERS[index % len(CONFLICT_BUILDERS)]
        spec = builder(index, domain_use)
        ok = _materialize(spec, destination / spec.name)
        index += 1
        if ok:
            created.append(spec.name)

    # Compatible controls
    compat_made = 0
    compat_index = 0
    while compat_made < n_compatible and compat_index < n_compatible * 3:
        domain = domains[compat_index % len(domains)]
        domain_use = f"{domain}_ok{compat_index}"
        domain_use = re.sub(r"[^a-z0-9_]", "_", domain_use)
        # Use high index band so names don't collide with conflicts
        spec = _compatible_orthogonal(10_000 + compat_index, domain_use)
        ok = _materialize(spec, destination / spec.name)
        compat_index += 1
        if ok:
            created.append(spec.name)
            compat_made += 1

    return created
