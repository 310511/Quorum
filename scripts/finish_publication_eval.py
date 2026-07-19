"""After hard_negatives raw eval finishes, run structured eval then publication-eval."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
HARD = ROOT / "data" / "pairs" / "hard_negatives"
COOPER_RAW = RESULTS / "run_20260718T182612Z_cooper_raw.json"
COOPER_STRUCT = RESULTS / "run_20260718T182612Z_cooper_structured.json"
RAW_CKPT = RESULTS / "hard_negatives_raw_checkpoint.json"
STRUCT_CKPT = RESULTS / "hard_negatives_structured_checkpoint.json"
RAW_LOG = RESULTS / "eval_hard_negatives_raw_live.log"


def _n_results(path: Path) -> int:
    if not path.exists():
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    return len(data.get("results") or [])


def _expected_pairs() -> int:
    if not HARD.exists():
        return 0
    return len(
        [p for p in HARD.iterdir() if p.is_dir() and (p / "label.json").exists()]
    )


def _run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def _raw_eval_finished() -> bool:
    if RAW_LOG.exists():
        text = RAW_LOG.read_text(encoding="utf-8", errors="replace")
        if "Full results saved to" in text:
            return True
    expected = _expected_pairs()
    return expected > 0 and _n_results(RAW_CKPT) >= expected


def _latest_raw_run() -> Path:
    preferred = RESULTS / "run_hard_negatives_raw_final.json"
    if preferred.exists() and _n_results(preferred) > 0:
        return preferred
    finals = sorted(RESULTS.glob("run_*Z.json"), key=lambda p: p.stat().st_mtime)
    for path in reversed(finals):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        pairs_dir = str(data.get("pairs_dir", "")).replace("\\", "/")
        if pairs_dir.endswith("hard_negatives") and data.get("input_mode") == "raw":
            if not data.get("partial"):
                return path
    if not RAW_CKPT.exists():
        raise FileNotFoundError(
            f"No raw hard-negatives results found (missing {RAW_CKPT})"
        )
    payload = json.loads(RAW_CKPT.read_text(encoding="utf-8"))
    payload["partial"] = False
    preferred.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return preferred


def main() -> None:
    expected = _expected_pairs()
    if expected == 0:
        raise SystemExit(f"No hard-negatives pairs under {HARD}")

    print(
        f"Waiting for raw hard-negatives eval to finish (~{expected} pairs)...",
        flush=True,
    )
    stable_hits = 0
    last_n = -1
    while not _raw_eval_finished():
        n = _n_results(RAW_CKPT)
        print(f"  raw progress: {n}/{expected}", flush=True)
        if n == last_n:
            stable_hits += 1
        else:
            stable_hits = 0
            last_n = n
        if n >= max(1, expected // 2) and stable_hits >= 30:
            print("  progress stalled; continuing with partial raw results", flush=True)
            break
        time.sleep(60)

    raw_final = _latest_raw_run()
    print(f"Using raw results: {raw_final} ({_n_results(raw_final)} pairs)", flush=True)

    print("Starting structured evaluation...", flush=True)
    _run(
        [
            sys.executable,
            "-m",
            "quorum",
            "--config",
            "config_hard.yaml",
            "eval",
            str(HARD),
            "--input-mode",
            "structured",
            "--checkpoint",
            str(STRUCT_CKPT),
        ]
    )

    struct_final = RESULTS / "run_hard_negatives_structured_final.json"
    if STRUCT_CKPT.exists():
        payload = json.loads(STRUCT_CKPT.read_text(encoding="utf-8"))
        payload["partial"] = False
        struct_final.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("Building publication package...", flush=True)
    _run(
        [
            sys.executable,
            "-m",
            "quorum",
            "publication-eval",
            "--cooper-raw",
            str(COOPER_RAW),
            "--cooper-structured",
            str(COOPER_STRUCT),
            "--hard-raw",
            str(raw_final),
            "--hard-structured",
            str(struct_final),
            "--pairs-dir",
            str(ROOT / "data" / "pairs"),
        ]
    )
    print("Done.", flush=True)


if __name__ == "__main__":
    main()
