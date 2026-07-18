"""Run configured models in parallel on a branch-pair conflict check."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from quorum.delta import PairDelta, compute_pair_delta
from quorum.models import ModelClient, ModelConfig, ModelResult, build_client

InputMode = Literal["raw", "structured"]


@dataclass
class BranchPair:
    name: str
    branch_a_diff: str
    branch_b_diff: str
    context: str
    input_mode: InputMode = "raw"
    structured_delta: PairDelta | None = None


@dataclass
class CommitteeRun:
    pair_name: str
    model_results: list[ModelResult] = field(default_factory=list)
    wall_clock_seconds: float = 0.0
    prompt: str = ""
    input_mode: InputMode = "raw"


def load_pair(pair_dir: Path, input_mode: InputMode = "raw") -> BranchPair:
    pair_dir = Path(pair_dir)
    if not pair_dir.is_dir():
        raise FileNotFoundError(f"pair directory not found: {pair_dir}")

    branch_a_path = pair_dir / "branch_a.diff"
    branch_b_path = pair_dir / "branch_b.diff"
    branch_a = branch_a_path.read_text(encoding="utf-8") if branch_a_path.exists() else ""
    branch_b = branch_b_path.read_text(encoding="utf-8") if branch_b_path.exists() else ""
    context_path = pair_dir / "context.md"
    context = context_path.read_text(encoding="utf-8") if context_path.exists() else ""

    structured_delta = None
    if input_mode == "structured":
        structured_delta = compute_pair_delta(pair_dir)

    return BranchPair(
        name=pair_dir.name,
        branch_a_diff=branch_a.strip(),
        branch_b_diff=branch_b.strip(),
        context=context.strip(),
        input_mode=input_mode,
        structured_delta=structured_delta,
    )


def build_prompt(pair: BranchPair) -> str:
    if pair.input_mode == "structured":
        return _build_structured_prompt(pair)
    return _build_raw_prompt(pair)


def _build_raw_prompt(pair: BranchPair) -> str:
    context_block = pair.context or "(no additional merge-base context provided)"
    return f"""Analyze whether Branch A and Branch B would conflict semantically if merged into the same codebase.

## Merge-base context
{context_block}

## Branch A diff
```diff
{pair.branch_a_diff}
```

## Branch B diff
```diff
{pair.branch_b_diff}
```

Question: If both branches are merged together (assuming no textual line overlap), will the combined result be logically correct, or is there a semantic conflict?

Return your answer as JSON with verdict, confidence, reasoning, and evidence."""


def _build_structured_prompt(pair: BranchPair) -> str:
    if pair.structured_delta is None:
        raise ValueError("structured input requested but no delta computed")

    delta_json = json.dumps(pair.structured_delta.to_dict(), indent=2)
    context_block = pair.context or "(see structured delta below)"
    return f"""Analyze whether Branch A and Branch B would conflict semantically if merged into the same codebase.

You are given a structured Python function-level delta (extracted via Tree-sitter AST parsing) for each branch relative to the merge-base — NOT raw diffs. Each changed function includes function_name, signature, and body_hash.

## Merge-base context
{context_block}

## Structured function delta (JSON)
```json
{delta_json}
```

The delta shows, per branch:
- added: new functions not present at merge-base
- removed: functions present at merge-base but absent on the branch
- changed: same function name with different signature and/or body_hash (includes `calls` made inside the new body)
- files: module-level import additions/removals per changed file
- cross_branch_links: symbols removed/renamed on one branch but still imported or called on the other

Pay special attention to:
- cross_branch_links (especially rename_stale_reference and removed_but_referenced)
- functions removed on one branch but still referenced/called on the other
- renames (removed + added with similar body_hash but different function_name)
- signature changes that break callers on the other branch

Question: If both branches are merged together (assuming no textual line overlap), will the combined result be logically correct, or is there a semantic conflict?

Return your answer as JSON with verdict, confidence, reasoning, and evidence."""


async def run_committee(
    pair: BranchPair,
    endpoint: str,
    models: list[ModelConfig],
    timeout: float,
    api_key: str | None = None,
    parallel: bool = False,
) -> CommitteeRun:
    prompt = build_prompt(pair)
    clients = [build_client(endpoint, model, timeout, api_key) for model in models]

    start = time.perf_counter()
    if parallel:
        results = await asyncio.gather(*(client.complete(prompt) for client in clients))
    else:
        results = []
        for client in clients:
            results.append(await client.complete(prompt))
    elapsed = time.perf_counter() - start

    return CommitteeRun(
        pair_name=pair.name,
        model_results=list(results),
        wall_clock_seconds=elapsed,
        prompt=prompt,
        input_mode=pair.input_mode,
    )
