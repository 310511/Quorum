"""In-memory function-level delta vs merge-base (Phase 1 — no graph DB)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from quorum.extract import FunctionInfo, extract_file_info, extract_from_tree, functions_by_name


@dataclass
class FunctionDelta:
    function_name: str
    file: str
    merge_base: FunctionInfo | None = None
    branch: FunctionInfo | None = None

    def to_dict(self) -> dict:
        result = {
            "function_name": self.function_name,
            "file": self.file,
            "merge_base": self.merge_base.to_dict() if self.merge_base else None,
            "branch": self.branch.to_dict() if self.branch else None,
        }
        if self.branch and self.branch.calls:
            result["calls"] = list(self.branch.calls)
        return result


@dataclass
class FileDelta:
    file: str
    imports_added: list[str] = field(default_factory=list)
    imports_removed: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "imports_added": self.imports_added,
            "imports_removed": self.imports_removed,
        }


@dataclass
class BranchDelta:
    added: list[FunctionInfo] = field(default_factory=list)
    removed: list[FunctionInfo] = field(default_factory=list)
    changed: list[FunctionDelta] = field(default_factory=list)
    files: list[FileDelta] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "added": [f.to_dict() for f in self.added],
            "removed": [f.to_dict() for f in self.removed],
            "changed": [c.to_dict() for c in self.changed],
            "files": [f.to_dict() for f in self.files],
        }


@dataclass
class CrossBranchLink:
    symbol: str
    link_type: str
    removed_on: str
    referenced_on: str
    file: str
    detail: str

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "type": self.link_type,
            "removed_on": self.removed_on,
            "referenced_on": self.referenced_on,
            "file": self.file,
            "detail": self.detail,
        }


@dataclass
class PairDelta:
    pair_name: str
    files: list[str]
    branch_a: BranchDelta
    branch_b: BranchDelta
    cross_branch_links: list[CrossBranchLink] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "pair": self.pair_name,
            "language": "python",
            "files": self.files,
            "branch_a": self.branch_a.to_dict(),
            "branch_b": self.branch_b.to_dict(),
            "cross_branch_links": [link.to_dict() for link in self.cross_branch_links],
        }


def _collect_py_paths(*roots: Path) -> list[str]:
    paths: set[str] = set()
    for root in roots:
        root = Path(root)
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            paths.add(path.relative_to(root).as_posix())
    return sorted(paths)


def _resolve_source(branch_dir: Path, merge_base_dir: Path, rel_path: str) -> str | None:
    branch_path = branch_dir / rel_path
    if branch_path.exists():
        return branch_path.read_text(encoding="utf-8")
    merge_path = merge_base_dir / rel_path
    if merge_path.exists():
        return merge_path.read_text(encoding="utf-8")
    return None


def _file_tree(branch_dir: Path, merge_base_dir: Path) -> tuple[dict[str, list[FunctionInfo]], dict[str, list[str]]]:
    rel_paths = _collect_py_paths(merge_base_dir, branch_dir)
    functions: dict[str, list[FunctionInfo]] = {}
    imports: dict[str, list[str]] = {}
    for rel in rel_paths:
        source = _resolve_source(branch_dir, merge_base_dir, rel)
        if source is None:
            continue
        fn_list, import_list = extract_file_info(source, rel)
        functions[rel] = fn_list
        imports[rel] = import_list
    return functions, imports


def _import_symbols(import_lines: list[str]) -> set[str]:
    symbols: set[str] = set()
    for line in import_lines:
        from_match = re.search(r"from\s+\S+\s+import\s+(.+)", line)
        if from_match:
            for part in from_match.group(1).split(","):
                name = part.strip().split(" as ")[0].strip()
                if name and name != "*":
                    symbols.add(name)
            continue
        import_match = re.search(r"^import\s+(.+)", line)
        if import_match:
            for part in import_match.group(1).split(","):
                name = part.strip().split(" as ")[0].strip().split(".")[0]
                if name:
                    symbols.add(name)
    return symbols


def _referenced_symbols(
    branch_delta: BranchDelta,
    branch_imports: dict[str, list[str]],
) -> dict[str, list[tuple[str, str]]]:
    refs: dict[str, list[tuple[str, str]]] = {}
    for file_delta in branch_delta.files:
        for imp in file_delta.imports_added:
            for sym in _import_symbols([imp]):
                refs.setdefault(sym, []).append((file_delta.file, f"import: {imp}"))
    for change in branch_delta.changed:
        if change.branch and change.branch.calls:
            for call in change.branch.calls:
                refs.setdefault(call, []).append((change.file, f"call in {change.function_name}"))
    for added in branch_delta.added:
        for call in added.calls:
            refs.setdefault(call, []).append((added.file, f"call in {added.function_name}"))
    return refs


def _file_import_delta(
    merge_imports: dict[str, list[str]],
    branch_imports: dict[str, list[str]],
) -> list[FileDelta]:
    deltas: list[FileDelta] = []
    for rel in sorted(set(merge_imports) | set(branch_imports)):
        base = set(merge_imports.get(rel, []))
        branch = set(branch_imports.get(rel, []))
        added = sorted(branch - base)
        removed = sorted(base - branch)
        if added or removed:
            deltas.append(FileDelta(file=rel, imports_added=added, imports_removed=removed))
    return deltas


def _diff_branch(
    merge_base: dict[str, list[FunctionInfo]],
    branch: dict[str, list[FunctionInfo]],
    merge_imports: dict[str, list[str]],
    branch_imports: dict[str, list[str]],
) -> BranchDelta:
    base_index = functions_by_name(merge_base)
    branch_index = functions_by_name(branch)
    base_keys = set(base_index)
    branch_keys = set(branch_index)

    added = [branch_index[k] for k in sorted(branch_keys - base_keys)]
    removed = [base_index[k] for k in sorted(base_keys - branch_keys)]

    changed: list[FunctionDelta] = []
    for key in sorted(base_keys & branch_keys):
        base_fn = base_index[key]
        branch_fn = branch_index[key]
        if base_fn.signature != branch_fn.signature or base_fn.body_hash != branch_fn.body_hash:
            changed.append(
                FunctionDelta(
                    function_name=base_fn.function_name,
                    file=base_fn.file,
                    merge_base=base_fn,
                    branch=branch_fn,
                )
            )

    return BranchDelta(
        added=added,
        removed=removed,
        changed=changed,
        files=_file_import_delta(merge_imports, branch_imports),
    )


def _cross_branch_links(
    branch_a: BranchDelta,
    branch_b: BranchDelta,
    branch_a_imports: dict[str, list[str]],
    branch_b_imports: dict[str, list[str]],
) -> list[CrossBranchLink]:
    links: list[CrossBranchLink] = []

    def check_pair(
        removed: set[str],
        added_same_branch: set[str],
        removed_fns: list[FunctionInfo],
        added_fns: list[FunctionInfo],
        refs: dict[str, list[tuple[str, str]]],
        removed_on: str,
        referenced_on: str,
    ) -> None:
        for symbol in sorted(removed):
            rename_target = None
            removed_fn = next((f for f in removed_fns if f.function_name == symbol), None)
            if removed_fn:
                for other_fn in added_fns:
                    if other_fn.body_hash == removed_fn.body_hash and other_fn.function_name != symbol:
                        rename_target = other_fn.function_name
                        break
            if symbol in refs:
                for file, detail in refs[symbol]:
                    links.append(
                        CrossBranchLink(
                            symbol=symbol,
                            link_type="rename_stale_reference" if rename_target else "removed_but_referenced",
                            removed_on=removed_on,
                            referenced_on=referenced_on,
                            file=file,
                            detail=(
                                f"{detail}; renamed to {rename_target} on {removed_on}"
                                if rename_target
                                else detail
                            ),
                        )
                    )

    refs_b = _referenced_symbols(branch_b, branch_b_imports)
    refs_a = _referenced_symbols(branch_a, branch_a_imports)
    check_pair(
        {fn.function_name for fn in branch_a.removed},
        {fn.function_name for fn in branch_a.added},
        branch_a.removed,
        branch_a.added,
        refs_b,
        "branch_a",
        "branch_b",
    )
    check_pair(
        {fn.function_name for fn in branch_b.removed},
        {fn.function_name for fn in branch_b.added},
        branch_b.removed,
        branch_b.added,
        refs_a,
        "branch_b",
        "branch_a",
    )
    return links


def compute_pair_delta(pair_dir: Path) -> PairDelta:
    pair_dir = Path(pair_dir)
    merge_base_dir = pair_dir / "merge_base"
    branch_a_dir = pair_dir / "branch_a"
    branch_b_dir = pair_dir / "branch_b"

    for name, path in (
        ("merge_base", merge_base_dir),
        ("branch_a", branch_a_dir),
        ("branch_b", branch_b_dir),
    ):
        if not path.is_dir():
            raise FileNotFoundError(
                f"{pair_dir.name}: missing {name}/ directory (required for structured input)"
            )

    merge_base = extract_from_tree(merge_base_dir)
    merge_imports = {
        rel: extract_file_info((merge_base_dir / rel).read_text(encoding="utf-8"), rel)[1]
        for rel in _collect_py_paths(merge_base_dir)
    }

    branch_a, branch_a_imports = _file_tree(branch_a_dir, merge_base_dir)
    branch_b, branch_b_imports = _file_tree(branch_b_dir, merge_base_dir)

    delta_a = _diff_branch(merge_base, branch_a, merge_imports, branch_a_imports)
    delta_b = _diff_branch(merge_base, branch_b, merge_imports, branch_b_imports)

    rel_paths = _collect_py_paths(merge_base_dir, branch_a_dir, branch_b_dir)
    return PairDelta(
        pair_name=pair_dir.name,
        files=rel_paths,
        branch_a=delta_a,
        branch_b=delta_b,
        cross_branch_links=_cross_branch_links(delta_a, delta_b, branch_a_imports, branch_b_imports),
    )
