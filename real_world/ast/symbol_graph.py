"""Symbol graph construction and branch intersection detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from real_world.ast.symbol_extractor import FileSymbols, SymbolInfo, symbol_fingerprint


@dataclass
class SymbolGraph:
    nodes: dict[str, SymbolInfo] = field(default_factory=dict)
    edges: list[tuple[str, str, str]] = field(default_factory=list)  # src, rel, dst

    def add_symbol(self, symbol: SymbolInfo) -> str:
        node_id = symbol_fingerprint(symbol)
        self.nodes[node_id] = symbol
        return node_id

    def add_edge(self, src: str, rel: str, dst: str) -> None:
        self.edges.append((src, rel, dst))

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "edges": [{"src": s, "rel": r, "dst": d} for s, r, d in self.edges],
        }


def build_graph(file_symbols: dict[str, FileSymbols]) -> SymbolGraph:
    graph = SymbolGraph()
    name_to_nodes: dict[str, list[str]] = {}

    for file_sym in file_symbols.values():
        for symbol in file_sym.all_symbols():
            node_id = graph.add_symbol(symbol)
            name_to_nodes.setdefault(symbol.name, []).append(node_id)
            if symbol.kind == "call":
                for target_id in name_to_nodes.get(symbol.name, []):
                    graph.add_edge(node_id, "calls", target_id)

    for file_sym in file_symbols.values():
        for symbol in file_sym.classes:
            src = symbol_fingerprint(symbol)
            for base in symbol.bases:
                for target_id in name_to_nodes.get(base, []):
                    graph.add_edge(src, "inherits", target_id)

    return graph


def _changed_symbols(
    base_symbols: dict[str, FileSymbols],
    branch_symbols: dict[str, FileSymbols],
) -> set[str]:
    changed: set[str] = set()
    all_files = set(base_symbols) | set(branch_symbols)
    for file_path in all_files:
        base = base_symbols.get(file_path)
        branch = branch_symbols.get(file_path)
        if base is None and branch is None:
            continue
        if base is None or branch is None:
            for sym in (branch or base).all_symbols():
                changed.add(sym.qualified_name)
            continue

        def index(symbols: FileSymbols) -> dict[tuple[str, str], SymbolInfo]:
            return {(s.kind, s.qualified_name): s for s in symbols.all_symbols()}

        base_idx = index(base)
        branch_idx = index(branch)
        for key in set(base_idx) | set(branch_idx):
            b = base_idx.get(key)
            a = branch_idx.get(key)
            if b is None or a is None:
                changed.add(key[1])
                continue
            if b.signature != a.signature or b.decorators != a.decorators:
                changed.add(key[1])
    return changed


def _call_targets(symbols: dict[str, FileSymbols]) -> set[str]:
    targets: set[str] = set()
    for file_sym in symbols.values():
        for call in file_sym.calls:
            targets.add(call.name)
    return targets


def _defined_names(symbols: dict[str, FileSymbols]) -> set[str]:
    names: set[str] = set()
    for file_sym in symbols.values():
        for sym in file_sym.functions + file_sym.classes + file_sym.methods:
            names.add(sym.name)
            names.add(sym.qualified_name)
    return names


@dataclass
class IntersectionResult:
    intersects: bool
    shared_files: list[str]
    shared_symbols: list[str]
    caller_callee_links: list[str]
    shared_classes: list[str]
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "intersects": self.intersects,
            "shared_files": self.shared_files,
            "shared_symbols": self.shared_symbols,
            "caller_callee_links": self.caller_callee_links,
            "shared_classes": self.shared_classes,
            "reasons": self.reasons,
        }


def detect_intersection(
    *,
    base_symbols: dict[str, FileSymbols],
    left_symbols: dict[str, FileSymbols],
    right_symbols: dict[str, FileSymbols],
    left_files: list[str],
    right_files: list[str],
) -> IntersectionResult:
    shared_files = sorted(set(left_files) & set(right_files))
    left_changed = _changed_symbols(base_symbols, left_symbols)
    right_changed = _changed_symbols(base_symbols, right_symbols)
    shared_symbols = sorted(left_changed & right_changed)

    left_calls = _call_targets(left_symbols)
    right_calls = _call_targets(right_symbols)
    left_defs = _defined_names(left_symbols)
    right_defs = _defined_names(right_symbols)

    caller_callee: set[str] = set()
    for sym in left_changed:
        name = sym.split(".")[-1]
        if name in right_calls:
            caller_callee.add(f"left defines/changes {sym}; right calls {name}")
        if name in right_defs:
            caller_callee.add(f"left changes {sym}; right defines {name}")
    for sym in right_changed:
        name = sym.split(".")[-1]
        if name in left_calls:
            caller_callee.add(f"right defines/changes {sym}; left calls {name}")
        if name in left_defs:
            caller_callee.add(f"right changes {sym}; left defines {name}")

    left_classes = {s.qualified_name for fs in left_symbols.values() for s in fs.classes}
    right_classes = {s.qualified_name for fs in right_symbols.values() for s in fs.classes}
    shared_classes = sorted((left_classes | left_changed) & (right_classes | right_changed))

    reasons: list[str] = []
    if shared_files:
        reasons.append("same_python_file")
    if shared_symbols:
        reasons.append("shared_symbol_change")
    if caller_callee:
        reasons.append("caller_callee_relationship")
    if shared_classes:
        reasons.append("shared_class_or_method")

    intersects = bool(shared_files or shared_symbols or caller_callee or shared_classes)
    return IntersectionResult(
        intersects=intersects,
        shared_files=shared_files,
        shared_symbols=shared_symbols,
        caller_callee_links=sorted(caller_callee),
        shared_classes=shared_classes,
        reasons=reasons,
    )
