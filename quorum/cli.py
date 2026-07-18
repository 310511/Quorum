"""CLI entry point for Quorum Phase 0."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

from quorum.adjudicate import AdjudicationResult, adjudicate
from quorum.baseline import BaselineRun, run_baseline
from quorum.committee import CommitteeRun, InputMode, load_pair, run_committee
from quorum.import_cooperbench import import_cooperbench_zip
from quorum.delta import compute_pair_delta
from quorum.models import ModelConfig

DEFAULT_CONFIG = Path("config.yaml")
RESULTS_DIR = Path("results")


def load_config(config_path: Path) -> dict:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"config not found: {path}")
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def parse_models(config: dict) -> list[ModelConfig]:
    return [
        ModelConfig(name=m["name"], role=m.get("role", "general"))
        for m in config.get("models", [])
    ]


def find_baseline_model(config: dict, models: list[ModelConfig]) -> ModelConfig:
    baseline_name = config.get("baseline_model")
    if not baseline_name:
        raise ValueError("config.yaml must set baseline_model")
    for model in models:
        if model.name == baseline_name:
            return model
    return ModelConfig(name=baseline_name, role="baseline")


def discover_pairs(pairs_dir: Path) -> list[Path]:
    pairs_dir = Path(pairs_dir)
    if not pairs_dir.is_dir():
        raise FileNotFoundError(f"pairs directory not found: {pairs_dir}")

    pairs = []
    for entry in sorted(pairs_dir.iterdir()):
        if not entry.is_dir():
            continue
        if (entry / "branch_a.diff").exists() or (
            (entry / "merge_base").is_dir() and (entry / "label.json").exists()
        ):
            pairs.append(entry)
    return pairs


def pair_language(pair_dir: Path) -> str | None:
    label = load_label(pair_dir)
    return label.get("language") if label else None


def resolve_input_mode(config: dict, override: InputMode | None) -> InputMode:
    if override:
        return override
    mode = config.get("input_mode", "raw")
    if mode not in ("raw", "structured"):
        raise ValueError(f"invalid input_mode: {mode!r} (expected 'raw' or 'structured')")
    return mode


def load_label(pair_dir: Path) -> dict | None:
    label_path = pair_dir / "label.json"
    if not label_path.exists():
        return None
    return json.loads(label_path.read_text(encoding="utf-8"))


def _verdict_from_baseline(run: BaselineRun) -> str:
    if run.result.outcome == "ok" and run.result.verdict:
        return run.result.verdict.verdict
    return "error"


def _print_model_result(label: str, result) -> None:
    print(f"\n--- {label} ---")
    if result.outcome != "ok" or not result.verdict:
        print(f"  ERROR: {result.error or 'unknown'}")
        return
    v = result.verdict
    print(f"  Verdict:    {v.verdict}")
    print(f"  Confidence: {v.confidence:.2f}")
    print(f"  Reasoning:  {v.reasoning}")
    if v.evidence:
        print("  Evidence:")
        for item in v.evidence:
            print(f"    - {item}")


def print_check_output(
    pair_name: str,
    ground_truth: str | None,
    baseline: BaselineRun,
    committee: CommitteeRun,
    adjudication: AdjudicationResult,
    input_mode: InputMode = "raw",
) -> None:
    print("=" * 72)
    print(f"Pair: {pair_name}  (input: {input_mode})")
    if ground_truth:
        print(f"Ground truth: {ground_truth}")
    print("=" * 72)

    print("\n## BASELINE (single model)")
    print(f"Model: {baseline.model_name}  ({baseline.wall_clock_seconds:.1f}s)")
    _print_model_result(baseline.model_name, baseline.result)
    baseline_verdict = _verdict_from_baseline(baseline)

    print("\n## COMMITTEE")
    print(f"Models: {len(committee.model_results)}  ({committee.wall_clock_seconds:.1f}s wall)")
    for result in committee.model_results:
        _print_model_result(result.model_name, result)

    print("\n## ADJUDICATION")
    print(f"  Final verdict:  {adjudication.final_verdict}")
    print(f"  Explanation:    {adjudication.explanation}")
    if adjudication.shared_evidence:
        print(f"  Shared identifiers: {adjudication.shared_evidence}")
    if adjudication.weak_evidence_models:
        print(f"  Weak evidence:    {', '.join(adjudication.weak_evidence_models)}")
    if adjudication.dissenting_models:
        print(f"  Dissenting:     {', '.join(adjudication.dissenting_models)}")
    if adjudication.failed_models:
        print(f"  Failed models:  {', '.join(adjudication.failed_models)}")

    print("\n## COMPARISON")
    committee_verdict = adjudication.final_verdict
    print(f"  Baseline:  {baseline_verdict}")
    print(f"  Committee: {committee_verdict}")
    if ground_truth:
        b_ok = baseline_verdict == ground_truth
        c_ok = committee_verdict == ground_truth
        print(f"  Baseline matches ground truth:  {'yes' if b_ok else 'no'}")
        print(f"  Committee matches ground truth: {'yes' if c_ok else 'no'}")


async def _run_pair(
    pair_dir: Path,
    config: dict,
    input_mode: InputMode,
) -> dict:
    if input_mode == "structured":
        lang = pair_language(pair_dir)
        if lang and lang != "python":
            raise ValueError(
                f"{pair_dir.name}: structured input is Python-only (language={lang}). "
                "Use --input-mode raw or filter pairs."
            )
    pair = load_pair(pair_dir, input_mode=input_mode)
    models = parse_models(config)
    baseline_model = find_baseline_model(config, models)
    endpoint = config["ollama_base_url"]
    timeout = float(config.get("time_budget_seconds", 90))
    api_key = config.get("api_key")
    parallel = bool(config.get("committee_parallel", False))

    baseline = await run_baseline(pair, endpoint, baseline_model, timeout, api_key)
    committee = await run_committee(
        pair, endpoint, models, timeout, api_key, parallel=parallel
    )
    structured_payload = (
        pair.structured_delta.to_dict() if pair.structured_delta else None
    )
    adjudication = adjudicate(
        committee.model_results,
        branch_a_diff=pair.branch_a_diff,
        branch_b_diff=pair.branch_b_diff,
        structured_delta=structured_payload,
    )
    label = load_label(pair_dir)
    ground_truth = label.get("ground_truth") if label else None

    return {
        "pair": pair.name,
        "input_mode": input_mode,
        "ground_truth": ground_truth,
        "baseline_verdict": _verdict_from_baseline(baseline),
        "committee_verdict": adjudication.final_verdict,
        "baseline": _serialize_baseline(baseline),
        "committee": _serialize_committee(committee),
        "adjudication": asdict(adjudication),
        "_baseline_run": baseline,
        "_committee_run": committee,
        "_adjudication": adjudication,
    }


async def run_check(
    pair_dir: Path,
    config_path: Path,
    input_mode: InputMode | None = None,
) -> dict:
    config = load_config(config_path)
    mode = resolve_input_mode(config, input_mode)
    result = await _run_pair(pair_dir, config, mode)
    print_check_output(
        result["pair"],
        result["ground_truth"],
        result["_baseline_run"],
        result["_committee_run"],
        result["_adjudication"],
        input_mode=mode,
    )
    result.pop("_baseline_run", None)
    result.pop("_committee_run", None)
    result.pop("_adjudication", None)
    return result


def _serialize_baseline(run: BaselineRun) -> dict:
    return {
        "model_name": run.model_name,
        "wall_clock_seconds": run.wall_clock_seconds,
        "result": asdict(run.result),
    }


def _serialize_committee(run: CommitteeRun) -> dict:
    return {
        "wall_clock_seconds": run.wall_clock_seconds,
        "model_results": [asdict(r) for r in run.model_results],
    }


def _accuracy(results: list[dict], key: str) -> tuple[int, int, int]:
    labeled = [r for r in results if r.get("ground_truth")]
    if not labeled:
        return 0, 0, 0
    correct = sum(1 for r in labeled if r.get(key) == r["ground_truth"])
    escalated = sum(1 for r in labeled if r.get(key) == "escalate")
    return correct, len(labeled), escalated


def print_eval_summary(results: list[dict], title: str = "EVAL SUMMARY") -> None:
    b_correct, total, _ = _accuracy(results, "baseline_verdict")
    c_correct, _, c_escalated = _accuracy(results, "committee_verdict")

    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)
    print(f"{'Pair':<24} {'Truth':<12} {'Baseline':<12} {'Committee':<12}")
    print("-" * 72)
    for row in results:
        truth = row.get("ground_truth") or "?"
        print(
            f"{row['pair']:<24} {truth:<12} "
            f"{row['baseline_verdict']:<12} {row['committee_verdict']:<12}"
        )
    print("-" * 72)
    if total:
        print(f"Baseline accuracy:  {b_correct}/{total} ({100 * b_correct / total:.1f}%)")
        print(
            f"Committee accuracy: {c_correct}/{total} ({100 * c_correct / total:.1f}%) "
            f"[{c_escalated} escalated]"
        )
    else:
        print("No labeled pairs found (missing label.json).")


def print_compare_summary(raw_results: list[dict], structured_results: list[dict]) -> None:
    print("\n" + "=" * 72)
    print("INPUT MODE COMPARISON (committee accuracy)")
    print("=" * 72)
    print(f"{'Pair':<20} {'Truth':<10} {'Raw':<12} {'Structured':<12}")
    print("-" * 72)
    structured_by_pair = {r["pair"]: r for r in structured_results}
    for raw in raw_results:
        structured = structured_by_pair.get(raw["pair"], {})
        print(
            f"{raw['pair']:<20} {raw.get('ground_truth') or '?':<10} "
            f"{raw.get('committee_verdict', '?'):<12} "
            f"{structured.get('committee_verdict', '?'):<12}"
        )
    print("-" * 72)
    _, total, _ = _accuracy(raw_results, "committee_verdict")
    raw_c, _, raw_esc = _accuracy(raw_results, "committee_verdict")
    struct_c, _, struct_esc = _accuracy(structured_results, "committee_verdict")
    if total:
        print(
            f"Raw committee:        {raw_c}/{total} ({100 * raw_c / total:.1f}%) "
            f"[{raw_esc} escalated]"
        )
        print(
            f"Structured committee: {struct_c}/{total} ({100 * struct_c / total:.1f}%) "
            f"[{struct_esc} escalated]"
        )


async def run_eval(
    pairs_dir: Path,
    config_path: Path,
    input_mode: InputMode | None = None,
    compare_inputs: bool = False,
) -> Path:
    pairs = discover_pairs(pairs_dir)
    if not pairs:
        raise FileNotFoundError(f"no pair folders found under {pairs_dir}")

    config = load_config(config_path)

    if compare_inputs:
        raw_results = []
        structured_results = []
        for pair_dir in pairs:
            print(f"\nRunning {pair_dir.name} (raw)...", flush=True)
            try:
                raw_results.append(await _run_pair(pair_dir, config, "raw"))
            except Exception as exc:
                print(f"  SKIP raw: {exc}", flush=True)
            print(f"Running {pair_dir.name} (structured)...", flush=True)
            try:
                structured_results.append(await _run_pair(pair_dir, config, "structured"))
            except Exception as exc:
                print(f"  SKIP structured: {exc}", flush=True)
        for row in raw_results + structured_results:
            row.pop("_baseline_run", None)
            row.pop("_committee_run", None)
            row.pop("_adjudication", None)
        print_eval_summary(raw_results, title="EVAL SUMMARY — RAW INPUT")
        print_eval_summary(structured_results, title="EVAL SUMMARY — STRUCTURED INPUT")
        print_compare_summary(raw_results, structured_results)
        results_payload = {
            "raw": raw_results,
            "structured": structured_results,
        }
        input_label = "compare"
    else:
        mode = resolve_input_mode(config, input_mode)
        results = []
        for pair_dir in pairs:
            print(f"\nRunning {pair_dir.name} ({mode})...", flush=True)
            try:
                row = await _run_pair(pair_dir, config, mode)
            except Exception as exc:
                print(f"  SKIP: {exc}", flush=True)
                continue
            row.pop("_baseline_run", None)
            row.pop("_committee_run", None)
            row.pop("_adjudication", None)
            results.append(row)
        print_eval_summary(results, title=f"EVAL SUMMARY — {mode.upper()} INPUT")
        results_payload = results
        input_label = mode

    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = RESULTS_DIR / f"run_{timestamp}.json"
    if compare_inputs:
        payload = {
            "timestamp": timestamp,
            "config_path": str(config_path),
            "pairs_dir": str(pairs_dir),
            "input_mode": input_label,
            "summary": {
                "raw_committee_accuracy": _accuracy(raw_results, "committee_verdict"),
                "structured_committee_accuracy": _accuracy(
                    structured_results, "committee_verdict"
                ),
            },
            "results": results_payload,
        }
    else:
        payload = {
            "timestamp": timestamp,
            "config_path": str(config_path),
            "pairs_dir": str(pairs_dir),
            "input_mode": input_label,
            "summary": {
                "baseline_accuracy": _accuracy(results, "baseline_verdict"),
                "committee_accuracy": _accuracy(results, "committee_verdict"),
            },
            "results": results_payload,
        }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nFull results saved to {out_path}")
    return out_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="quorum",
        description="Quorum Phase 0 — semantic merge conflict detection",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to config.yaml (default: config.yaml)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    input_mode_kwargs = {
        "choices": ("raw", "structured"),
        "default": None,
        "help": "Override config input_mode (raw diff vs structured AST delta)",
    }

    sub = parser.add_subparsers(dest="command", required=True)

    extract_parser = sub.add_parser(
        "extract", help="Print Tree-sitter function delta JSON for a pair"
    )
    extract_parser.add_argument("pair_dir", type=Path, help="Path to a pair folder")

    import_parser = sub.add_parser(
        "import-cooperbench",
        help="Import pairs from cooperbench_merge_pairs.zip into data/pairs/",
    )
    import_parser.add_argument(
        "zip_path",
        type=Path,
        nargs="?",
        default=Path("cooperbench_merge_pairs.zip"),
        help="Path to CooperBench zip (default: cooperbench_merge_pairs.zip)",
    )
    import_parser.add_argument(
        "--dest",
        type=Path,
        default=Path("data/pairs"),
        help="Destination directory (default: data/pairs)",
    )

    check_parser = sub.add_parser("check", help="Run baseline + committee on one pair")
    check_parser.add_argument("pair_dir", type=Path, help="Path to a pair folder")
    check_parser.add_argument("--input-mode", **input_mode_kwargs)

    eval_parser = sub.add_parser("eval", help="Evaluate all labeled pairs in a directory")
    eval_parser.add_argument(
        "pairs_dir",
        type=Path,
        nargs="?",
        default=Path("data/pairs"),
        help="Directory containing pair subfolders (default: data/pairs)",
    )
    eval_parser.add_argument("--input-mode", **input_mode_kwargs)
    eval_parser.add_argument(
        "--compare-inputs",
        action="store_true",
        help="Run each pair with raw and structured input; print side-by-side accuracy",
    )

    # Also accept --input-mode before subcommand: quorum --input-mode structured check ...
    parser.add_argument("--input-mode", **input_mode_kwargs)

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    try:
        if args.command == "extract":
            delta = compute_pair_delta(args.pair_dir)
            print(json.dumps(delta.to_dict(), indent=2))
        elif args.command == "import-cooperbench":
            imported = import_cooperbench_zip(args.zip_path, args.dest)
            print(f"Imported {len(imported)} pairs into {args.dest}")
            for name in imported:
                print(f"  - {name}")
        elif args.command == "check":
            asyncio.run(
                run_check(args.pair_dir, args.config, input_mode=args.input_mode)
            )
        elif args.command == "eval":
            asyncio.run(
                run_eval(
                    args.pairs_dir,
                    args.config,
                    input_mode=args.input_mode,
                    compare_inputs=args.compare_inputs,
                )
            )
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        if args.verbose:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
