"""Single-model baseline for comparison against the committee."""

from __future__ import annotations

import time
from dataclasses import dataclass

from quorum.committee import BranchPair, build_prompt
from quorum.models import ModelClient, ModelConfig, ModelResult, build_client


@dataclass
class BaselineRun:
    pair_name: str
    model_name: str
    result: ModelResult
    wall_clock_seconds: float = 0.0
    prompt: str = ""


async def run_baseline(
    pair: BranchPair,
    endpoint: str,
    model: ModelConfig,
    timeout: float,
    api_key: str | None = None,
) -> BaselineRun:
    prompt = build_prompt(pair)
    client = build_client(endpoint, model, timeout, api_key)

    start = time.perf_counter()
    result = await client.complete(prompt)
    elapsed = time.perf_counter() - start

    return BaselineRun(
        pair_name=pair.name,
        model_name=model.name,
        result=result,
        wall_clock_seconds=elapsed,
        prompt=prompt,
    )
