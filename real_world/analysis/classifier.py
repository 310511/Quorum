"""Phase 4: semantic category classification from AST/diff signals."""

from __future__ import annotations

import logging
import re
from typing import Any

from real_world.common import append_jsonl, load_existing_ids, progress, read_jsonl
from real_world.config import CANDIDATES_JSONL, CLASSIFIED_JSONL, SEMANTIC_CATEGORIES
from real_world.filters.initial_filter import diff_text
from real_world.config import REPO_BY_SLUG

logger = logging.getLogger(__name__)

CATEGORY_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("Routing", re.compile(r"@(app|router|route|get|post|put|delete|patch)\b|APIRouter|urlpatterns", re.I)),
    ("Middleware", re.compile(r"Middleware|middleware|add_middleware", re.I)),
    ("Dependency Injection", re.compile(r"Depends\(|inject|provide_", re.I)),
    ("ORM", re.compile(r"\b(Model|Column|relationship|ForeignKey|Mapped\[|declarative_base)\b")),
    ("Transaction", re.compile(r"session\.commit|transaction|rollback|atomic\(", re.I)),
    ("DataFrame semantics", re.compile(r"DataFrame|Series|groupby|merge\(|concat\(", re.I)),
    ("Serialization", re.compile(r"json\.|serialize|deserialize|model_dump|to_dict|from_dict", re.I)),
    ("Caching", re.compile(r"cache|lru_cache|memoize|TTL", re.I)),
    ("Async", re.compile(r"async def|await |asyncio|AsyncSession", re.I)),
    ("Inheritance", re.compile(r"class\s+\w+\s*\(|super\(\)", re.I)),
    ("Exception contract", re.compile(r"raise \w+|except \w+|HTTPException|ValidationError", re.I)),
    ("Validation", re.compile(r"validate|validator|Field\(|constr|model_validator", re.I)),
    ("Default parameter", re.compile(r"def\s+\w+\([^)]*=\s*[^,)]+", re.I)),
    ("Function signature", re.compile(r"def\s+\w+\([^)]*\)", re.I)),
    ("Return value", re.compile(r"return |->\s*\w+|Annotated\[", re.I)),
    ("State mutation", re.compile(r"self\.\w+\s*=|global \w+|nonlocal \w+", re.I)),
    ("Ownership", re.compile(r"__enter__|__exit__|close\(|dispose\(|acquire|release", re.I)),
    ("Resource lifetime", re.compile(r"contextmanager|__del__|cleanup|shutdown", re.I)),
    ("API change", re.compile(r"__all__|public api|deprecated|DeprecationWarning", re.I)),
]


def classify_candidate(record: dict[str, Any]) -> dict[str, Any]:
    repository = record["repository"]
    spec = REPO_BY_SLUG[repository]
    repo = spec.clone_path
    merge_base = record["merge_base"]
    parent_a = record["parent_a"]
    parent_b = record["parent_b"]

    combined_diff = "\n".join(
        [
            diff_text(repo, merge_base, parent_a),
            diff_text(repo, merge_base, parent_b),
        ]
    )
    scores: dict[str, int] = {cat: 0 for cat in SEMANTIC_CATEGORIES}
    for category, pattern in CATEGORY_RULES:
        matches = len(pattern.findall(combined_diff))
        if matches:
            scores[category] += matches

    symbols_text = " ".join(record.get("affected_symbols", []))
    for category, pattern in CATEGORY_RULES:
        if pattern.search(symbols_text):
            scores[category] += 2

    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    best_category, best_score = ranked[0]
    if best_score == 0:
        best_category = "Other"

    return {
        **record,
        "semantic_category": best_category,
        "category_scores": scores,
    }


def classify_all(*, resume: bool = True) -> dict[str, int]:
    candidates = read_jsonl(CANDIDATES_JSONL)
    existing = load_existing_ids(CLASSIFIED_JSONL) if resume else set()
    kept = 0

    for record in progress(candidates, desc="classify", total=len(candidates)):
        if record["id"] in existing:
            continue
        classified = classify_candidate(record)
        append_jsonl(CLASSIFIED_JSONL, classified)
        existing.add(record["id"])
        kept += 1

    logger.info("Classified %d candidates", kept)
    return {"classified": kept}
