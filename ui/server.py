"""
Quorum Demo UI — lightweight Flask server.

Runs from the repo root so `quorum` package is importable.
Usage (from repo root):
    python ui/server.py
    # or via the helper:
    bash ui/run.sh
"""

from __future__ import annotations

import asyncio
import json
import sys
import traceback
from dataclasses import asdict
from pathlib import Path

# Ensure repo root is on sys.path when launched from ui/
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS

import yaml
from quorum.adjudicate_v2 import adjudicate_v2
from quorum.baseline import run_baseline
from quorum.committee import BranchPair, build_prompt, run_committee
from quorum.models import ModelConfig, normalize_verdict

app = Flask(__name__, static_folder=Path(__file__).parent, static_url_path="")
# Allow both the served origin and file:// (which browsers send as "null")
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173", "null"],
     supports_credentials=False)

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin", "")
    # file:// pages arrive with Origin: null — allow them explicitly
    if origin in ("null", "http://localhost:5173", "http://127.0.0.1:5173") or not origin:
        response.headers["Access-Control-Allow-Origin"] = origin or "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route("/api/analyze", methods=["OPTIONS"])
@app.route("/api/config", methods=["OPTIONS"])
def preflight():
    resp = app.make_default_options_response()
    resp.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp

CONFIG_PATH = ROOT / "config.yaml"


# ── helpers ────────────────────────────────────────────────────────────────────

def _load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"config.yaml not found at {CONFIG_PATH}")
    with CONFIG_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _parse_models(config: dict) -> list[ModelConfig]:
    return [
        ModelConfig(name=m["name"], role=m.get("role", "general"))
        for m in config.get("models", [])
    ]


def _find_baseline(config: dict, models: list[ModelConfig]) -> ModelConfig:
    name = config.get("baseline_model")
    for m in models:
        if m.name == name:
            return m
    return ModelConfig(name=name or models[0].name, role="baseline")


def _safe_asdict(obj) -> dict:
    """dataclass → dict, tolerating nested non-dataclass objects."""
    try:
        return asdict(obj)
    except Exception:
        return {"error": str(obj)}


# ── routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(Path(__file__).parent, "index.html")


@app.route("/api/config", methods=["GET"])
def get_config():
    """Return the current model config so the UI can display it."""
    try:
        config = _load_config()
        models = _parse_models(config)
        return jsonify({
            "models": [{"name": m.name, "role": m.role} for m in models],
            "baseline_model": config.get("baseline_model"),
            "input_mode": config.get("input_mode", "raw"),
            "committee_parallel": config.get("committee_parallel", False),
            "time_budget_seconds": config.get("time_budget_seconds", 90),
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    POST body (JSON):
        branch_a_diff   str  required
        branch_b_diff   str  required
        context         str  optional
        input_mode      "raw" | "structured"   optional (overrides config)
        pair_name       str  optional label shown in results

    Returns a Server-Sent Events stream so the UI can show each model result
    as it arrives.
    """
    body = request.get_json(force=True, silent=True) or {}

    branch_a = (body.get("branch_a_diff") or "").strip()
    branch_b = (body.get("branch_b_diff") or "").strip()
    context  = (body.get("context") or "").strip()
    pair_name = (body.get("pair_name") or "demo").strip()

    if not branch_a or not branch_b:
        return jsonify({"error": "branch_a_diff and branch_b_diff are required"}), 400

    try:
        config = _load_config()
    except Exception as exc:
        return jsonify({"error": f"Could not load config.yaml: {exc}"}), 500

    cfg_input_mode = config.get("input_mode", "raw")
    input_mode = body.get("input_mode") or cfg_input_mode
    if input_mode not in ("raw", "structured"):
        input_mode = "raw"

    # structured mode requires real source files; degrade gracefully
    if input_mode == "structured":
        input_mode = "raw"   # diff-only UI can't run tree-sitter without source trees
        degraded = True
    else:
        degraded = False

    pair = BranchPair(
        name=pair_name,
        branch_a_diff=branch_a,
        branch_b_diff=branch_b,
        context=context,
        input_mode=input_mode,
        structured_delta=None,
    )

    models   = _parse_models(config)
    baseline_model = _find_baseline(config, models)
    endpoint = config["ollama_base_url"]
    timeout  = float(config.get("time_budget_seconds", 90))
    api_key  = config.get("api_key")
    parallel = bool(config.get("committee_parallel", False))
    prompt   = build_prompt(pair)

    def event_stream():
        def send(event: str, data: dict) -> str:
            return f"event: {event}\ndata: {json.dumps(data)}\n\n"

        # ── meta ──────────────────────────────────────────────────────────────
        yield send("meta", {
            "pair_name": pair_name,
            "input_mode": input_mode,
            "degraded_to_raw": degraded,
            "models": [{"name": m.name, "role": m.role} for m in models],
            "baseline_model": baseline_model.name,
            "prompt_preview": prompt[:600] + ("…" if len(prompt) > 600 else ""),
        })

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # ── baseline ──────────────────────────────────────────────────────
            yield send("status", {"message": f"Querying baseline model ({baseline_model.name})…"})
            baseline_run = loop.run_until_complete(
                run_baseline(pair, endpoint, baseline_model, timeout, api_key)
            )
            b_result = baseline_run.result
            b_verdict_raw = (
                b_result.verdict.verdict if b_result.outcome == "ok" and b_result.verdict else "error"
            )
            yield send("baseline", {
                "model_name": baseline_run.model_name,
                "wall_clock_seconds": round(baseline_run.wall_clock_seconds, 2),
                "outcome": b_result.outcome,
                "verdict": b_verdict_raw,
                "confidence": b_result.verdict.confidence if b_result.verdict else None,
                "reasoning": b_result.verdict.reasoning if b_result.verdict else None,
                "evidence": b_result.verdict.evidence if b_result.verdict else [],
                "error": b_result.error,
            })

            # ── committee — run one model at a time so UI streams progressively ──
            yield send("status", {"message": f"Querying {len(models)} committee models…"})

            committee_results = []
            if parallel:
                # Run in parallel but collect all at once
                from quorum.committee import run_committee as _run_committee
                committee_run = loop.run_until_complete(
                    _run_committee(pair, endpoint, models, timeout, api_key, parallel=True)
                )
                for r in committee_run.model_results:
                    committee_results.append(r)
                    yield send("model_result", {
                        "model_name": r.model_name,
                        "role": r.role,
                        "outcome": r.outcome,
                        "verdict": r.verdict.verdict if r.verdict else None,
                        "confidence": r.verdict.confidence if r.verdict else None,
                        "reasoning": r.verdict.reasoning if r.verdict else None,
                        "evidence": r.verdict.evidence if r.verdict else [],
                        "elapsed_seconds": round(r.elapsed_seconds, 2),
                        "error": r.error,
                    })
            else:
                from quorum.models import build_client
                for model in models:
                    yield send("status", {"message": f"Querying {model.name}…"})
                    client = build_client(endpoint, model, timeout, api_key)
                    r = loop.run_until_complete(client.complete(prompt))
                    committee_results.append(r)
                    yield send("model_result", {
                        "model_name": r.model_name,
                        "role": r.role,
                        "outcome": r.outcome,
                        "verdict": r.verdict.verdict if r.verdict else None,
                        "confidence": r.verdict.confidence if r.verdict else None,
                        "reasoning": r.verdict.reasoning if r.verdict else None,
                        "evidence": r.verdict.evidence if r.verdict else [],
                        "elapsed_seconds": round(r.elapsed_seconds, 2),
                        "error": r.error,
                    })

            # ── adjudication ──────────────────────────────────────────────────
            yield send("status", {"message": "Running evidence-weighted adjudication…"})
            adj = adjudicate_v2(
                committee_results,
                branch_a_diff=branch_a,
                branch_b_diff=branch_b,
                structured_delta=None,
            )
            yield send("adjudication", {
                "final_verdict": adj.final_verdict,
                "explanation": adj.explanation,
                "agreeing_models": adj.agreeing_models,
                "dissenting_models": adj.dissenting_models,
                "failed_models": adj.failed_models,
                "weak_evidence_models": adj.weak_evidence_models,
                "shared_evidence": adj.shared_evidence,
                "evidence_overlap_score": round(adj.evidence_overlap_score, 3),
                "decision_rule": adj.decision_rule,
                "rationale_scores": adj.rationale_scores,
                "baseline_verdict": b_verdict_raw,
            })

            yield send("done", {"message": "Analysis complete."})

        except Exception:
            yield send("error", {"message": traceback.format_exc()})
        finally:
            loop.close()

    return Response(event_stream(), mimetype="text/event-stream",
                    headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})


if __name__ == "__main__":
    print("=" * 60)
    print("  Quorum Demo UI")
    print(f"  http://localhost:5173")
    print(f"  Config: {CONFIG_PATH}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5173, debug=False, threaded=True)
