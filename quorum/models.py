"""Provider-agnostic async client for OpenAI-compatible chat completion endpoints."""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Literal

import httpx

logger = logging.getLogger(__name__)

VerdictLabel = Literal["compatible", "conflict"]
ModelOutcome = Literal["ok", "error"]

SYSTEM_PROMPT = """You are a code review expert analyzing whether two independent git branch changes would conflict semantically when merged.

A semantic conflict means the branches do not overlap on the same lines (no textual git conflict), but the merged result would be logically broken — e.g. one branch renames a function while the other still calls the old name, or incompatible API changes.

Respond with JSON only, no markdown fences, using this exact schema:
{
  "verdict": "compatible" | "conflict",
  "confidence": <float 0.0-1.0>,
  "reasoning": "<string explaining the verdict>",
  "evidence": ["<specific lines, function names, or behaviors cited as evidence>"]
}

Be conservative: if you are unsure, use verdict "conflict" with lower confidence and explain the uncertainty in reasoning.

CRITICAL: verdict must be exactly the lowercase string "conflict" or "compatible" — no other words (not "Conflicting", "incompatible", etc.)."""


@dataclass
class ModelConfig:
    name: str
    role: str = "general"


@dataclass
class VerdictResponse:
    verdict: VerdictLabel
    confidence: float
    reasoning: str
    evidence: list[str]


@dataclass
class ModelResult:
    model_name: str
    role: str
    outcome: ModelOutcome
    verdict: VerdictResponse | None = None
    error: str | None = None
    elapsed_seconds: float = 0.0
    raw_content: str | None = None


@dataclass
class ModelClient:
    endpoint: str
    model_name: str
    role: str = "general"
    timeout: float = 90.0
    api_key: str | None = None
    max_retries: int = 2

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def complete(self, user_prompt: str) -> ModelResult:
        start = time.perf_counter()
        last_error: str | None = None
        last_raw: str | None = None
        # gemma4 sometimes returns "{}" under json_object mode on long prompts
        json_modes = [True] * self.max_retries + [False]

        for attempt, json_mode in enumerate(json_modes):
            try:
                raw = await self._call_api(user_prompt, json_mode=json_mode)
                last_raw = raw
                parsed = _parse_verdict_json(raw)
                elapsed = time.perf_counter() - start
                return ModelResult(
                    model_name=self.model_name,
                    role=self.role,
                    outcome="ok",
                    verdict=parsed,
                    elapsed_seconds=elapsed,
                    raw_content=raw,
                )
            except asyncio.TimeoutError:
                last_error = f"timeout after {self.timeout}s"
                logger.warning("%s: %s (attempt %d)", self.model_name, last_error, attempt + 1)
            except (json.JSONDecodeError, ValueError) as exc:
                last_error = f"malformed JSON: {exc}"
                logger.warning(
                    "%s: %s (attempt %d, json_mode=%s)",
                    self.model_name,
                    last_error,
                    attempt + 1,
                    json_mode,
                )
            except httpx.TimeoutException as exc:
                last_error = f"timeout after {self.timeout}s ({type(exc).__name__})"
                logger.warning("%s: %s (attempt %d)", self.model_name, last_error, attempt + 1)
            except httpx.HTTPError as exc:
                last_error = f"HTTP error: {exc}"
                logger.warning("%s: %s (attempt %d)", self.model_name, last_error, attempt + 1)
                break
            except Exception as exc:
                last_error = str(exc)
                logger.warning("%s: %s (attempt %d)", self.model_name, last_error, attempt + 1)
                break

        elapsed = time.perf_counter() - start
        return ModelResult(
            model_name=self.model_name,
            role=self.role,
            outcome="error",
            error=last_error or "unknown error",
            elapsed_seconds=elapsed,
            raw_content=last_raw,
        )

    async def _call_api(self, user_prompt: str, *, json_mode: bool = True) -> str:
        user_content = user_prompt
        if not json_mode:
            user_content = (
                user_prompt
                + "\n\nRespond with ONLY a single JSON object (no markdown fences) with keys: "
                "verdict, confidence, reasoning, evidence."
            )
        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.1,
            "max_tokens": 4096,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.endpoint.rstrip('/')}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        choices = data.get("choices") or []
        if not choices:
            raise ValueError("API returned no choices")
        message = choices[0].get("message") or {}
        content = message.get("content")
        if not content:
            # Some Ollama reasoning models put output in reasoning field
            content = message.get("reasoning")
        if not content:
            raise ValueError("API returned empty content")
        return content.strip()


def _normalize_verdict(raw: Any) -> VerdictLabel | None:
    if raw is None:
        return None
    text = str(raw).strip().lower().replace("-", "_").replace(" ", "_")
    compatible = {
        "compatible",
        "compatible_merge",
        "clean_merge",
        "no_conflict",
        "no_conflicts",
        "ok",
        "safe",
        "mergeable",
    }
    conflict = {
        "conflict",
        "conflicting",
        "semantic_conflict",
        "incompatible",
        "clash",
        "has_conflict",
    }
    if text in compatible:
        return "compatible"
    if text in conflict:
        return "conflict"
    if "logically_correct" in text or text in {"correct", "mergeable", "fine", "valid"}:
        return "compatible"
    if "logically_incorrect" in text or "logically_broken" in text or "broken" in text:
        return "conflict"
    if "conflict" in text and "no_conflict" not in text:
        return "conflict"
    if "compat" in text or "clean_merge" in text:
        return "compatible"
    return None


def _extract_verdict_field(data: dict) -> Any:
    for key in ("verdict", "Verdict", "result", "decision", "label", "classification", "status"):
        if key in data:
            return data[key]
    return None


def _parse_verdict_json(raw: str) -> VerdictResponse:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    # Some models wrap JSON in prose — grab first {...} block
    if not cleaned.startswith("{"):
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)

    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")

    verdict = _normalize_verdict(_extract_verdict_field(data))
    if verdict is None:
        raise ValueError(f"invalid verdict: {_extract_verdict_field(data)!r}")

    confidence_raw = data.get("confidence", data.get("score", 0.0))
    try:
        confidence = float(confidence_raw)
    except (TypeError, ValueError):
        confidence = 0.5
    confidence = max(0.0, min(1.0, confidence))

    reasoning = data.get("reasoning") or data.get("explanation") or data.get("analysis")
    if not isinstance(reasoning, str) or not reasoning.strip():
        raise ValueError("reasoning must be a non-empty string")

    evidence = data.get("evidence", data.get("evidence_list", []))
    if isinstance(evidence, str):
        evidence = [evidence]
    if not isinstance(evidence, list):
        raise ValueError("evidence must be a list")
    normalized_evidence: list[str] = []
    for item in evidence:
        if not item:
            continue
        if isinstance(item, dict):
            normalized_evidence.append(json.dumps(item, sort_keys=True))
        else:
            normalized_evidence.append(str(item))
    evidence = normalized_evidence

    return VerdictResponse(
        verdict=verdict,
        confidence=confidence,
        reasoning=reasoning.strip(),
        evidence=evidence,
    )


def build_client(
    endpoint: str,
    model: ModelConfig,
    timeout: float,
    api_key: str | None = None,
) -> ModelClient:
    return ModelClient(
        endpoint=endpoint,
        model_name=model.name,
        role=model.role,
        timeout=timeout,
        api_key=api_key,
    )
