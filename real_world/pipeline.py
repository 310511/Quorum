"""Unified CLI for the real-world semantic merge dataset pipeline."""

from __future__ import annotations

import argparse
import sys

from real_world.analysis.agreement import build_agreement_report
from real_world.analysis.classifier import classify_all
from real_world.analysis.freeze import freeze_dataset
from real_world.analysis.heuristics import run_heuristics
from real_world.ast.candidate_detector import detect_all
from real_world.common import setup_logging, write_json
from real_world.config import REAL_WORLD_ROOT
from real_world.filters.initial_filter import filter_all
from real_world.miners.merge_miner import mine_all
from real_world.review.annotation_server import serve
from real_world.review.package_generator import generate_packages
from real_world.review.queue_generator import build_review_queue
from real_world.review.quorum_export import materialize_examples


def cmd_mine(args: argparse.Namespace) -> int:
    counts = mine_all(repos=args.repos, since=args.since, limit=args.limit, resume=not args.rebuild)
    write_json(REAL_WORLD_ROOT / "mine_stats.json", counts)
    print(counts)
    return 0


def cmd_filter(args: argparse.Namespace) -> int:
    stats = filter_all(resume=not args.rebuild)
    print(stats)
    return 0


def cmd_detect(args: argparse.Namespace) -> int:
    stats = detect_all(resume=not args.rebuild)
    print(stats)
    return 0


def cmd_classify(args: argparse.Namespace) -> int:
    stats = classify_all(resume=not args.rebuild)
    print(stats)
    return 0


def cmd_packages(args: argparse.Namespace) -> int:
    count = generate_packages(limit=args.limit)
    print({"packages": count})
    return 0


def cmd_heuristics(args: argparse.Namespace) -> int:
    stats = run_heuristics(resume=not args.rebuild)
    print(stats)
    return 0


def cmd_queue(args: argparse.Namespace) -> int:
    count = build_review_queue(limit=args.limit)
    print({"queue_rows": count})
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    serve(host=args.host, port=args.port)
    return 0


def cmd_agreement(args: argparse.Namespace) -> int:
    report = build_agreement_report()
    print(report)
    return 0


def cmd_materialize(args: argparse.Namespace) -> int:
    stats = materialize_examples(only_annotated=args.only_annotated)
    print(stats)
    return 0


def cmd_freeze(args: argparse.Namespace) -> int:
    stats = freeze_dataset(require_dual_agreement=args.require_agreement)
    print(stats)
    return 0


def cmd_run_all(args: argparse.Namespace) -> int:
    phases = [
        ("mine", lambda: mine_all(repos=args.repos, since=args.since, limit=args.limit, resume=not args.rebuild)),
        ("filter", lambda: filter_all(resume=not args.rebuild)),
        ("detect", lambda: detect_all(resume=not args.rebuild)),
        ("classify", lambda: classify_all(resume=not args.rebuild)),
        ("heuristics", lambda: run_heuristics(resume=not args.rebuild)),
        ("packages", lambda: generate_packages(limit=args.package_limit)),
        ("queue", lambda: build_review_queue(limit=args.queue_limit)),
    ]
    for index, (name, fn) in enumerate(phases, start=1):
        if args.start_phase and index < args.start_phase:
            continue
        print(f"\n=== Phase {index}: {name} ===", file=sys.stderr)
        result = fn()
        print(result)
    print("\nNext steps:", file=sys.stderr)
    print("  real-world-pipeline serve --port 8765", file=sys.stderr)
    print("  real-world-pipeline agreement && real-world-pipeline freeze", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Real-world semantic merge dataset pipeline")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    mine = sub.add_parser("mine", help="Phase 1 — clone repos and mine merge commits")
    mine.add_argument("--repos", nargs="*", help="Repository slugs (default: all six)")
    mine.add_argument("--since", help="Git --since filter, e.g. 2020-01-01")
    mine.add_argument("--limit", type=int, help="Max merge commits per repo")
    mine.add_argument("--rebuild", action="store_true", help="Disable resume; re-process all")
    mine.set_defaults(func=cmd_mine)

    filt = sub.add_parser("filter", help="Phase 2 — filter to executable Python merges")
    filt.add_argument("--rebuild", action="store_true")
    filt.set_defaults(func=cmd_filter)

    detect = sub.add_parser("detect", help="Phase 3 — AST symbol intersection candidates")
    detect.add_argument("--rebuild", action="store_true")
    detect.set_defaults(func=cmd_detect)

    classify = sub.add_parser("classify", help="Phase 4 — semantic category classification")
    classify.add_argument("--rebuild", action="store_true")
    classify.set_defaults(func=cmd_classify)

    packages = sub.add_parser("packages", help="Phase 5 — materialize candidate packages")
    packages.add_argument("--limit", type=int, help="Max packages to write")
    packages.set_defaults(func=cmd_packages)

    heur = sub.add_parser("heuristics", help="Phase 6 — conflict heuristics (no labels)")
    heur.add_argument("--rebuild", action="store_true")
    heur.set_defaults(func=cmd_heuristics)

    queue = sub.add_parser("queue", help="Phase 7 — build review_queue.csv")
    queue.add_argument("--limit", type=int, help="Max rows (default: all)")
    queue.set_defaults(func=cmd_queue)

    srv = sub.add_parser("serve", help="Phase 8 — annotation web UI")
    srv.add_argument("--host", default="127.0.0.1")
    srv.add_argument("--port", type=int, default=8765)
    srv.set_defaults(func=cmd_serve)

    agree = sub.add_parser("agreement", help="Phase 9 — reviewer agreement report")
    agree.set_defaults(func=cmd_agreement)

    materialize = sub.add_parser(
        "materialize",
        help="Export candidates to Quorum pair layout (dataset/real_world/examples/)",
    )
    materialize.add_argument(
        "--only-annotated",
        action="store_true",
        help="Export only human-annotated candidates",
    )
    materialize.set_defaults(func=cmd_materialize)

    freeze = sub.add_parser("freeze", help="Phase 10 — freeze annotated dataset")
    freeze.add_argument("--require-agreement", action="store_true")
    freeze.set_defaults(func=cmd_freeze)

    run_all = sub.add_parser("run-all", help="Run phases 1–7 sequentially")
    run_all.add_argument("--repos", nargs="*")
    run_all.add_argument("--since")
    run_all.add_argument("--limit", type=int)
    run_all.add_argument("--package-limit", type=int)
    run_all.add_argument("--queue-limit", type=int, default=250)
    run_all.add_argument("--start-phase", type=int, choices=range(1, 8))
    run_all.add_argument("--rebuild", action="store_true")
    run_all.set_defaults(func=cmd_run_all)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logging("real_world", verbose=args.verbose)
    return args.func(args)
