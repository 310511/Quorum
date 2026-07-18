"""Tree-sitter based Python function extraction (Phase 1)."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import tree_sitter_python as tspython
from tree_sitter import Language, Node, Parser

PY_LANGUAGE = Language(tspython.language())
_PARSER = Parser(PY_LANGUAGE)


@dataclass(frozen=True)
class FunctionInfo:
    function_name: str
    signature: str
    body_hash: str
    file: str
    start_line: int
    calls: tuple[str, ...] = ()
    identifiers: tuple[str, ...] = ()
    control_flow: tuple[str, ...] = ()
    decorators: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return asdict(self)


def _normalize_body(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _body_hash(body_text: str) -> str:
    normalized = _normalize_body(body_text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def _node_text(source: bytes, node: Node) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8")


def _function_name(node: Node, source: bytes, prefix: str = "") -> str | None:
    name_node = node.child_by_field_name("name")
    if name_node is None:
        return None
    name = _node_text(source, name_node)
    return f"{prefix}.{name}" if prefix else name


def _call_name(node: Node, source: bytes) -> str | None:
    if node.type == "call":
        fn = node.child_by_field_name("function")
        if fn is None:
            return None
        if fn.type == "identifier":
            return _node_text(source, fn)
        if fn.type == "attribute":
            attr = fn.child_by_field_name("attribute")
            if attr:
                return _node_text(source, attr)
    return None


def _extract_calls(node: Node, source: bytes, out: set[str]) -> None:
    name = _call_name(node, source)
    if name:
        out.add(name)
    for child in node.children:
        _extract_calls(child, source, out)


_CONTROL_FLOW_TYPES = frozenset(
    {
        "if_statement",
        "for_statement",
        "while_statement",
        "try_statement",
        "with_statement",
        "match_statement",
        "return_statement",
        "raise_statement",
        "yield",
        "await",
        "break_statement",
        "continue_statement",
        "list_comprehension",
        "set_comprehension",
        "dictionary_comprehension",
        "generator_expression",
    }
)


def _extract_identifiers_and_control_flow(
    node: Node,
    source: bytes,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    identifiers: set[str] = set()
    control_flow: Counter[str] = Counter()

    def walk(current: Node) -> None:
        if current.type == "identifier":
            identifiers.add(_node_text(source, current))
        if current.type in _CONTROL_FLOW_TYPES:
            control_flow[current.type] += 1
        for child in current.children:
            walk(child)

    walk(node)
    flow_summary = tuple(
        f"{node_type}:{count}" for node_type, count in sorted(control_flow.items())
    )
    return tuple(sorted(identifiers)), flow_summary


def _decorators(node: Node, source: bytes) -> tuple[str, ...]:
    parent = node.parent
    if parent is None or parent.type != "decorated_definition":
        return ()
    return tuple(
        _node_text(source, child).strip()
        for child in parent.children
        if child.type == "decorator"
    )


def _extract_imports(source: str) -> list[str]:
    source_bytes = source.encode("utf-8")
    tree = _PARSER.parse(source_bytes)
    imports: list[str] = []

    def walk(node: Node) -> None:
        if node.type == "import_statement":
            imports.append(_node_text(source_bytes, node).strip())
        elif node.type == "import_from_statement":
            imports.append(_node_text(source_bytes, node).strip())
        for child in node.children:
            walk(child)

    for child in tree.root_node.children:
        walk(child)
    return sorted(set(imports))


def extract_module_summary(source: str) -> dict[str, list[str]]:
    """Return deterministic module-level API and identifier summaries."""
    source_bytes = source.encode("utf-8")
    tree = _PARSER.parse(source_bytes)
    classes: set[str] = set()
    assignments: set[str] = set()
    identifiers: set[str] = set()

    def assignment_names(node: Node) -> None:
        if node.type == "identifier":
            assignments.add(_node_text(source_bytes, node))
            return
        for child in node.children:
            assignment_names(child)

    def walk(node: Node) -> None:
        if node.type == "identifier":
            identifiers.add(_node_text(source_bytes, node))
        if node.type == "class_definition":
            name = node.child_by_field_name("name")
            superclasses = node.child_by_field_name("superclasses")
            if name:
                class_api = _node_text(source_bytes, name)
                if superclasses:
                    class_api += _node_text(source_bytes, superclasses)
                classes.add(class_api)
        if node.parent == tree.root_node:
            assignment_node = node
            if node.type == "expression_statement":
                assignment_node = next(
                    (
                        child
                        for child in node.children
                        if child.type in {"assignment", "augmented_assignment"}
                    ),
                    node,
                )
            if assignment_node.type in {"assignment", "augmented_assignment"}:
                left = assignment_node.child_by_field_name("left")
                if left:
                    assignment_names(left)
        for child in node.children:
            walk(child)

    walk(tree.root_node)
    return {
        "imports": _extract_imports(source),
        "classes": sorted(classes),
        "assignments": sorted(assignments),
        "identifiers": sorted(identifiers),
    }


def _extract_from_node(
    node: Node,
    source: bytes,
    rel_path: str,
    prefix: str,
    out: list[FunctionInfo],
) -> None:
    if node.type == "function_definition":
        name = _function_name(node, source, prefix)
        if name:
            params = node.child_by_field_name("parameters")
            body = node.child_by_field_name("body")
            if params and body:
                header = source[node.start_byte : body.start_byte].decode("utf-8").strip()
                signature = header if header.endswith(":") else header + ":"
                body_text = _node_text(source, body)
                calls: set[str] = set()
                _extract_calls(body, source, calls)
                identifiers, control_flow = _extract_identifiers_and_control_flow(
                    body, source
                )
                out.append(
                    FunctionInfo(
                        function_name=name,
                        signature=signature,
                        body_hash=_body_hash(body_text),
                        file=rel_path,
                        start_line=node.start_point[0] + 1,
                        calls=tuple(sorted(calls)),
                        identifiers=identifiers,
                        control_flow=control_flow,
                        decorators=_decorators(node, source),
                    )
                )
        nested_prefix = name or prefix
        for child in node.children:
            if child.type == "block":
                for block_child in child.children:
                    _extract_from_node(block_child, source, rel_path, nested_prefix, out)
        return

    for child in node.children:
        _extract_from_node(child, source, rel_path, prefix, out)


def extract_functions(source: str, rel_path: str) -> list[FunctionInfo]:
    source_bytes = source.encode("utf-8")
    tree = _PARSER.parse(source_bytes)
    functions: list[FunctionInfo] = []
    for child in tree.root_node.children:
        _extract_from_node(child, source_bytes, rel_path, "", functions)
    return functions


def extract_file_info(source: str, rel_path: str) -> tuple[list[FunctionInfo], list[str]]:
    return extract_functions(source, rel_path), _extract_imports(source)


def extract_from_tree(root: Path) -> dict[str, list[FunctionInfo]]:
    root = Path(root)
    by_file: dict[str, list[FunctionInfo]] = {}
    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        source = path.read_text(encoding="utf-8")
        by_file[rel] = extract_functions(source, rel)
    return by_file


def functions_by_name(by_file: dict[str, list[FunctionInfo]]) -> dict[str, FunctionInfo]:
    indexed: dict[str, FunctionInfo] = {}
    for rel_path, functions in by_file.items():
        for fn in functions:
            key = f"{rel_path}::{fn.function_name}"
            indexed[key] = fn
    return indexed
