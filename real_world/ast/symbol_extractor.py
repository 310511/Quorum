"""Python AST symbol extraction for merge analysis."""

from __future__ import annotations

import ast
import hashlib
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from real_world.common import git_output
from real_world.config import REPO_BY_SLUG

logger = logging.getLogger(__name__)


@dataclass
class SymbolInfo:
    kind: str  # function | method | class | import | call | inheritance
    name: str
    qualified_name: str
    file: str
    lineno: int
    signature: str = ""
    bases: tuple[str, ...] = ()
    decorators: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FileSymbols:
    file: str
    functions: list[SymbolInfo] = field(default_factory=list)
    classes: list[SymbolInfo] = field(default_factory=list)
    methods: list[SymbolInfo] = field(default_factory=list)
    imports: list[SymbolInfo] = field(default_factory=list)
    calls: list[SymbolInfo] = field(default_factory=list)
    inheritance: list[SymbolInfo] = field(default_factory=list)

    def all_symbols(self) -> list[SymbolInfo]:
        return (
            self.functions
            + self.classes
            + self.methods
            + self.imports
            + self.calls
            + self.inheritance
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "functions": [s.to_dict() for s in self.functions],
            "classes": [s.to_dict() for s in self.classes],
            "methods": [s.to_dict() for s in self.methods],
            "imports": [s.to_dict() for s in self.imports],
            "calls": [s.to_dict() for s in self.calls],
            "inheritance": [s.to_dict() for s in self.inheritance],
        }


class _SymbolVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str, source: str) -> None:
        self.file_path = file_path
        self.source = source
        self.functions: list[SymbolInfo] = []
        self.classes: list[SymbolInfo] = []
        self.methods: list[SymbolInfo] = []
        self.imports: list[SymbolInfo] = []
        self.calls: list[SymbolInfo] = []
        self.inheritance: list[SymbolInfo] = []
        self._class_stack: list[str] = []

    def _sig(self, node: ast.AST) -> str:
        try:
            segment = ast.get_source_segment(self.source, node) or ""
            first_line = segment.splitlines()[0] if segment else ""
            return first_line.strip()
        except Exception:
            return ""

    def _decorators(self, node: ast.AST) -> tuple[str, ...]:
        deco_list = getattr(node, "decorator_list", []) or []
        names: list[str] = []
        for deco in deco_list:
            if isinstance(deco, ast.Name):
                names.append(deco.id)
            elif isinstance(deco, ast.Attribute):
                names.append(deco.attr)
            elif isinstance(deco, ast.Call):
                if isinstance(deco.func, ast.Name):
                    names.append(deco.func.id)
                elif isinstance(deco.func, ast.Attribute):
                    names.append(deco.func.attr)
        return tuple(names)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(
                SymbolInfo(
                    kind="import",
                    name=alias.asname or alias.name,
                    qualified_name=alias.name,
                    file=self.file_path,
                    lineno=node.lineno,
                )
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            qname = f"{module}.{alias.name}" if module else alias.name
            self.imports.append(
                SymbolInfo(
                    kind="import",
                    name=alias.asname or alias.name,
                    qualified_name=qname,
                    file=self.file_path,
                    lineno=node.lineno,
                )
            )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        qname = ".".join([*self._class_stack, node.name]) if self._class_stack else node.name
        bases = tuple(self._base_name(base) for base in node.bases)
        info = SymbolInfo(
            kind="class",
            name=node.name,
            qualified_name=qname,
            file=self.file_path,
            lineno=node.lineno,
            signature=self._sig(node),
            bases=bases,
            decorators=self._decorators(node),
        )
        self.classes.append(info)
        for base in bases:
            if base:
                self.inheritance.append(
                    SymbolInfo(
                        kind="inheritance",
                        name=base,
                        qualified_name=f"{qname} -> {base}",
                        file=self.file_path,
                        lineno=node.lineno,
                    )
                )
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record_function(node, is_async=True)

    def _record_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, *, is_async: bool = False) -> None:
        if self._class_stack:
            qname = ".".join([*self._class_stack, node.name])
            kind = "method"
            bucket = self.methods
        else:
            qname = node.name
            kind = "function"
            bucket = self.functions
        info = SymbolInfo(
            kind=kind,
            name=node.name,
            qualified_name=qname,
            file=self.file_path,
            lineno=node.lineno,
            signature=self._sig(node),
            decorators=self._decorators(node),
            metadata={"async": is_async},
        )
        bucket.append(info)
        self._extract_calls(node, owner=qname)

    def _extract_calls(self, node: ast.AST, owner: str) -> None:
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                call_name = self._call_name(child.func)
                if call_name:
                    self.calls.append(
                        SymbolInfo(
                            kind="call",
                            name=call_name,
                            qualified_name=f"{owner} -> {call_name}",
                            file=self.file_path,
                            lineno=getattr(child, "lineno", 0),
                        )
                    )

    def _call_name(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return None

    def _base_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        if isinstance(node, ast.Subscript):
            return self._base_name(node.value)
        return ""


def parse_python_source(file_path: str, source: str) -> FileSymbols | None:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        logger.debug("Skipping unparsable %s: %s", file_path, exc)
        return None
    visitor = _SymbolVisitor(file_path, source)
    visitor.visit(tree)
    return FileSymbols(
        file=file_path,
        functions=visitor.functions,
        classes=visitor.classes,
        methods=visitor.methods,
        imports=visitor.imports,
        calls=visitor.calls,
        inheritance=visitor.inheritance,
    )


def file_content_at_commit(repo: Path, commit: str, rel_path: str) -> str | None:
    try:
        return git_output(repo, "show", f"{commit}:{rel_path}")
    except Exception:
        return None


def extract_symbols_at_commit(
    repository: str,
    commit: str,
    files: list[str],
) -> dict[str, FileSymbols]:
    spec = REPO_BY_SLUG[repository]
    repo = spec.clone_path
    out: dict[str, FileSymbols] = {}
    for rel_path in files:
        source = file_content_at_commit(repo, commit, rel_path)
        if source is None:
            continue
        parsed = parse_python_source(rel_path, source)
        if parsed is not None:
            out[rel_path] = parsed
    return out


def symbol_fingerprint(symbol: SymbolInfo) -> str:
    payload = f"{symbol.kind}:{symbol.qualified_name}:{symbol.file}:{symbol.signature}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
