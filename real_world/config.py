"""Configuration for the real-world semantic merge dataset pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = ROOT / "dataset"
REPOS_DIR = DATASET_ROOT / "repos"
REAL_WORLD_ROOT = DATASET_ROOT / "real_world"
CANDIDATES_DIR = DATASET_ROOT / "real_world_candidates"

# Phase output artifacts
MERGES_JSONL = REAL_WORLD_ROOT / "merges.jsonl"
FILTERED_JSONL = REAL_WORLD_ROOT / "filtered.jsonl"
CANDIDATES_JSONL = REAL_WORLD_ROOT / "candidates.jsonl"
CLASSIFIED_JSONL = REAL_WORLD_ROOT / "classified.jsonl"
HEURISTICS_JSONL = REAL_WORLD_ROOT / "heuristics.jsonl"
REVIEW_QUEUE_CSV = REAL_WORLD_ROOT / "review_queue.csv"
ANNOTATIONS_JSONL = REAL_WORLD_ROOT / "annotations.jsonl"
REVIEWER_A_JSONL = REAL_WORLD_ROOT / "reviewer_A.jsonl"
REVIEWER_B_JSONL = REAL_WORLD_ROOT / "reviewer_B.jsonl"
AGREEMENT_REPORT = REAL_WORLD_ROOT / "agreement_report.md"
FROZEN_ROOT = REAL_WORLD_ROOT / "examples"
FROZEN_LABELS = REAL_WORLD_ROOT / "labels.json"
FROZEN_METADATA = REAL_WORLD_ROOT / "metadata.json"
FROZEN_README = REAL_WORLD_ROOT / "README.md"

SEMANTIC_CATEGORIES = (
    "API change",
    "Function signature",
    "Default parameter",
    "Return value",
    "Exception contract",
    "State mutation",
    "Ownership",
    "Validation",
    "ORM",
    "Transaction",
    "Dependency Injection",
    "Routing",
    "Middleware",
    "Async",
    "Inheritance",
    "Caching",
    "Resource lifetime",
    "DataFrame semantics",
    "Serialization",
    "Other",
)


@dataclass(frozen=True)
class RepositorySpec:
    name: str
    url: str
    slug: str

    @property
    def clone_path(self) -> Path:
        return REPOS_DIR / self.slug


REPOSITORIES: tuple[RepositorySpec, ...] = (
    RepositorySpec("requests", "https://github.com/psf/requests", "requests"),
    RepositorySpec("pandas", "https://github.com/pandas-dev/pandas", "pandas"),
    RepositorySpec("pydantic", "https://github.com/pydantic/pydantic", "pydantic"),
    RepositorySpec(
        "sqlalchemy", "https://github.com/sqlalchemy/sqlalchemy", "sqlalchemy"
    ),
    RepositorySpec("fastapi", "https://github.com/fastapi/fastapi", "fastapi"),
    RepositorySpec("django", "https://github.com/django/django", "django"),
)

REPO_BY_SLUG = {repo.slug: repo for repo in REPOSITORIES}

# Path segments that indicate non-executable / out-of-scope changes.
SKIP_PATH_FRAGMENTS = (
    "/docs/",
    "/doc/",
    "/documentation/",
    "/.github/",
    "/.circleci/",
    "/.travis/",
    "/.azure/",
    "/locale/",
    "/locales/",
    "/translations/",
    "/i18n/",
    "/release-notes/",
    "/changelog/",
)

SKIP_PATH_PREFIXES = (
    "docs/",
    "doc/",
    ".github/",
    ".circleci/",
    ".travis/",
    "locale/",
    "locales/",
    "translations/",
)

SKIP_BASENAMES = frozenset(
    {
        "readme.md",
        "readme.rst",
        "readme.txt",
        "changelog.md",
        "changelog.rst",
        "changes.md",
        "history.md",
        "contributing.md",
        "authors.md",
        "license",
        "license.md",
        "code_of_conduct.md",
        "security.md",
    }
)

TEST_PATH_MARKERS = (
    "/tests/",
    "/test/",
    "/testing/",
    "/testsuite/",
    "/testcases/",
)

DEPENDENCY_BUMP_FILES = frozenset(
    {
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "requirements.txt",
        "requirements-dev.txt",
        "requirements_test.txt",
        "Pipfile",
        "poetry.lock",
        "uv.lock",
    }
)
