"""Phase 1: clone repositories and mine merge commits."""

from __future__ import annotations

import hashlib
import logging
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from real_world.common import append_jsonl, git_output, git_output_optional, load_existing_ids, progress, run_git
from real_world.config import MERGES_JSONL, REPOSITORIES, REPOS_DIR, RepositorySpec

logger = logging.getLogger(__name__)


@dataclass
class MergeRecord:
    id: str
    repository: str
    repository_url: str
    merge_commit: str
    parent_a: str
    parent_b: str
    merge_base: str
    merge_subject: str
    merge_author_date: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def make_merge_id(repository: str, merge_commit: str, parent_a: str, parent_b: str) -> str:
    raw = f"{repository}:{merge_commit}:{parent_a}:{parent_b}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def ensure_repo(spec: RepositorySpec) -> Path:
    REPOS_DIR.mkdir(parents=True, exist_ok=True)
    dest = spec.clone_path
    if not (dest / ".git").exists():
        logger.info("Cloning %s -> %s", spec.url, dest)
        subprocess.run(["git", "clone", spec.url, str(dest)], check=True)
    return dest


def list_merge_commits(repo: Path, *, since: str | None = None, limit: int | None = None) -> list[str]:
    args = ["log", "--merges", "--pretty=format:%H"]
    if since:
        args.extend([f"--since={since}"])
    if limit:
        args.append(f"-n{limit}")
    output = git_output(repo, *args)
    if not output:
        return []
    return output.splitlines()


def parse_merge_commit(repo: Path, merge_sha: str, spec: RepositorySpec) -> MergeRecord | None:
    parents = git_output(repo, "rev-parse", f"{merge_sha}^@").split()
    if len(parents) < 2:
        return None
    parent_a, parent_b = parents[0], parents[1]
    if parent_a == parent_b:
        logger.debug("Skipping merge %s: duplicate parents", merge_sha[:12])
        return None

    merge_base = git_output_optional(repo, "merge-base", parent_a, parent_b)
    if not merge_base:
        logger.warning(
            "Skipping merge %s in %s: no merge-base between parents "
            "(likely unrelated-history / cross-repo merge)",
            merge_sha[:12],
            spec.slug,
        )
        return None
    subject = git_output(repo, "show", "-s", "--format=%s", merge_sha)
    author_date = git_output(repo, "show", "-s", "--format=%aI", merge_sha)
    merge_id = make_merge_id(spec.slug, merge_sha, parent_a, parent_b)
    return MergeRecord(
        id=merge_id,
        repository=spec.slug,
        repository_url=spec.url,
        merge_commit=merge_sha,
        parent_a=parent_a,
        parent_b=parent_b,
        merge_base=merge_base,
        merge_subject=subject,
        merge_author_date=author_date,
    )


def mine_repository(
    spec: RepositorySpec,
    *,
    since: str | None = None,
    limit: int | None = None,
    resume: bool = True,
) -> list[MergeRecord]:
    repo = ensure_repo(spec)
    existing = load_existing_ids(MERGES_JSONL) if resume else set()
    merges = list_merge_commits(repo, since=since, limit=limit)
    records: list[MergeRecord] = []

    for merge_sha in progress(merges, desc=f"mine {spec.slug}", total=len(merges)):
        parsed = parse_merge_commit(repo, merge_sha, spec)
        if parsed is None:
            continue
        if parsed.id in existing:
            continue
        append_jsonl(MERGES_JSONL, parsed.to_dict())
        existing.add(parsed.id)
        records.append(parsed)

    logger.info("Mined %d new merges from %s (%d total scanned)", len(records), spec.slug, len(merges))
    return records


def mine_all(
    *,
    repos: list[str] | None = None,
    since: str | None = None,
    limit: int | None = None,
    resume: bool = True,
) -> dict[str, int]:
    MERGES_JSONL.parent.mkdir(parents=True, exist_ok=True)
    selected = REPOSITORIES
    if repos:
        wanted = set(repos)
        selected = tuple(r for r in REPOSITORIES if r.slug in wanted)

    counts: dict[str, int] = {}
    for spec in selected:
        mined = mine_repository(spec, since=since, limit=limit, resume=resume)
        counts[spec.slug] = len(mined)
    return counts
