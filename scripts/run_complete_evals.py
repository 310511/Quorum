"""Orchestrate live evals on existing datasets and emit complete reports.

Sequence (serialized to avoid Ollama contention):
  1. Finish blind_eval raw (200) if still running / resume
  2. Finish hard_compatible (twins) raw (102) resume
  3. Blind structured (200)
  4. Twins structured (102)
  5. Score all corpora + write combined report

Already-complete corpora (CooperBench, hard_negatives) are scored immediately.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PY = sys.executable


def _n(path: Path) -> int:
    if not path.exists():
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    return len(data.get("results") or [])


def _expected(pairs_dir: Path) -> int:
    if not pairs_dir.exists():
        return 0
    return len(
        [p for p in pairs_dir.iterdir() if p.is_dir() and (p / "label.json").exists()]
    )


def _run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def _eval_raw(pairs: Path, checkpoint: Path, log: Path, expected: int) -> Path:
    """Resume/finish a raw eval; return final JSON path."""
    final = RESULTS / f"run_{pairs.name}_raw_final.json"
    if _n(checkpoint) >= expected and expected > 0:
        print(f"[skip] {pairs.name} raw already complete ({_n(checkpoint)}/{expected})")
    else:
        print(f"[eval] {pairs.name} raw {_n(checkpoint)}/{expected}", flush=True)
        cmd = [
            PY,
            "-m",
            "quorum",
            "--config",
            "config_hard.yaml",
            "eval",
            str(pairs),
            "--input-mode",
            "raw",
            "--checkpoint",
            str(checkpoint),
        ]
        if checkpoint.exists() and _n(checkpoint) > 0:
            cmd.extend(["--resume-from", str(checkpoint)])
        with log.open("a", encoding="utf-8") as fh:
            fh.write(f"\n--- resume {time.strftime('%Y-%m-%dT%H:%M:%SZ')} ---\n")
            proc = subprocess.Popen(
                cmd,
                cwd=ROOT,
                stdout=fh,
                stderr=subprocess.STDOUT,
                text=True,
            )
            while proc.poll() is None:
                n = _n(checkpoint)
                print(f"  {pairs.name} raw progress: {n}/{expected}", flush=True)
                time.sleep(60)
            if proc.returncode != 0:
                raise RuntimeError(f"eval failed for {pairs}: exit {proc.returncode}")

    # Finalize checkpoint into run_*_raw_final.json
    if checkpoint.exists():
        payload = json.loads(checkpoint.read_text(encoding="utf-8"))
        payload["partial"] = False
        final.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return final
    # Prefer latest matching run_*Z.json
    for path in sorted(RESULTS.glob("run_*Z.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        pairs_dir = str(data.get("pairs_dir", "")).replace("\\", "/")
        if pairs.name in pairs_dir and data.get("input_mode") == "raw":
            return path
    raise FileNotFoundError(f"No raw results for {pairs}")


def _eval_structured(pairs: Path, checkpoint: Path, log: Path, expected: int) -> Path:
    final = RESULTS / f"run_{pairs.name}_structured_final.json"
    if _n(checkpoint) >= expected and expected > 0:
        print(f"[skip] {pairs.name} structured already complete")
    else:
        print(f"[eval] {pairs.name} structured {_n(checkpoint)}/{expected}", flush=True)
        cmd = [
            PY,
            "-m",
            "quorum",
            "--config",
            "config_hard.yaml",
            "eval",
            str(pairs),
            "--input-mode",
            "structured",
            "--checkpoint",
            str(checkpoint),
        ]
        if checkpoint.exists() and _n(checkpoint) > 0:
            cmd.extend(["--resume-from", str(checkpoint)])
        with log.open("a", encoding="utf-8") as fh:
            fh.write(f"\n--- structured {time.strftime('%Y-%m-%dT%H:%M:%SZ')} ---\n")
            proc = subprocess.Popen(
                cmd,
                cwd=ROOT,
                stdout=fh,
                stderr=subprocess.STDOUT,
                text=True,
            )
            while proc.poll() is None:
                n = _n(checkpoint)
                print(f"  {pairs.name} structured progress: {n}/{expected}", flush=True)
                time.sleep(60)
            if proc.returncode != 0:
                raise RuntimeError(
                    f"structured eval failed for {pairs}: exit {proc.returncode}"
                )
    if checkpoint.exists():
        payload = json.loads(checkpoint.read_text(encoding="utf-8"))
        payload["partial"] = False
        final.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return final
    raise FileNotFoundError(f"No structured results for {pairs}")


def _score_blind(run: Path) -> None:
    _run([PY, "scripts/score_blind_eval.py", str(run)])


def _score_simple(run: Path, name: str) -> dict:
    """Quick 3-system score for any labeled run JSON."""
    from math import sqrt

    data = json.loads(run.read_text(encoding="utf-8"))
    rows = data["results"]

    def norm(v):
        if not v:
            return None
        v = str(v).lower()
        if v == "conflict":
            return "conflict"
        if v in ("no_conflict", "compatible", "clean_merge"):
            return "no_conflict"
        if v == "escalate":
            return "escalate"
        return v

    def majority(row):
        votes = []
        for mr in row["committee"]["model_results"]:
            if mr.get("outcome") == "ok" and mr.get("verdict"):
                votes.append(norm(mr["verdict"].get("verdict")))
        c = Counter(v for v in votes if v in {"conflict", "no_conflict"})
        if not c:
            return "escalate"
        top = c.most_common()
        if len(top) > 1 and top[0][1] == top[1][1]:
            return "escalate"
        return top[0][0]

    def conf(y_true, y_pred):
        tp = fp = tn = fn = esc = 0
        for t, p in zip(y_true, y_pred):
            if p not in ("conflict", "no_conflict"):
                esc += 1
                if t == "conflict":
                    fn += 1
                else:
                    fp += 1
                continue
            if t == "conflict" and p == "conflict":
                tp += 1
            elif t == "no_conflict" and p == "conflict":
                fp += 1
            elif t == "no_conflict" and p == "no_conflict":
                tn += 1
            else:
                fn += 1
        n = len(y_true)
        prec = tp / (tp + fp) if (tp + fp) else 0
        rec = tp / (tp + fn) if (tp + fn) else 0
        spec = tn / (tn + fp) if (tn + fp) else 0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0
        bal = 0.5 * (rec + spec)
        denom = sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        mcc = ((tp * tn) - (fp * fn)) / denom if denom else 0
        return {
            "TP": tp,
            "FP": fp,
            "TN": tn,
            "FN": fn,
            "escalate": esc,
            "accuracy": (tp + tn) / n if n else 0,
            "precision": prec,
            "recall": rec,
            "specificity": spec,
            "f1": f1,
            "balanced_accuracy": bal,
            "mcc": mcc,
            "coverage": (n - esc) / n if n else 0,
            "escalation_rate": esc / n if n else 0,
        }

    y = [norm(r["ground_truth"]) for r in rows]
    systems = {
        "Baseline": [norm(r["baseline_verdict"]) for r in rows],
        "Majority": [majority(r) for r in rows],
        "Committee": [
            norm((r.get("adjudication") or {}).get("final_verdict") or r.get("committee_verdict"))
            for r in rows
        ],
    }
    metrics = {k: conf(y, v) for k, v in systems.items()}
    payload = {
        "corpus": name,
        "run": run.name,
        "n": len(rows),
        "labels": dict(Counter(y)),
        "systems": metrics,
    }
    out = RESULTS / f"report_{name}.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md = [
        f"# Report — {name}",
        "",
        f"- Run: `{run.name}`",
        f"- N={len(rows)} · labels={dict(Counter(y))}",
        "",
        "| System | Acc | Prec | Recall | Spec | F1 | BalAcc | MCC | Cov | Esc |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for k, m in metrics.items():
        md.append(
            f"| {k} | {m['accuracy']:.1%} | {m['precision']:.1%} | {m['recall']:.1%} | "
            f"{m['specificity']:.1%} | {m['f1']:.1%} | {m['balanced_accuracy']:.1%} | "
            f"{m['mcc']:.2f} | {m['coverage']:.1%} | {m['escalation_rate']:.1%} |"
        )
    md.append("")
    (RESULTS / f"report_{name}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[report] {name}: wrote {out.name} + report_{name}.md")
    return payload


def _combined_report(parts: list[dict]) -> None:
    md = [
        "# Complete Evaluation Report — Existing Datasets",
        "",
        f"Generated: {time.strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "## Corpora",
        "",
    ]
    for p in parts:
        md.append(f"### {p['corpus']} (N={p['n']})")
        md.append("")
        md.append(f"Labels: `{p['labels']}` · Run: `{p['run']}`")
        md.append("")
        md.append("| System | Acc | Prec | Recall | Spec | F1 | BalAcc | MCC | Esc |")
        md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
        for k, m in p["systems"].items():
            md.append(
                f"| {k} | {m['accuracy']:.1%} | {m['precision']:.1%} | {m['recall']:.1%} | "
                f"{m['specificity']:.1%} | {m['f1']:.1%} | {m['balanced_accuracy']:.1%} | "
                f"{m['mcc']:.2f} | {m['escalation_rate']:.1%} |"
            )
        md.append("")
    out = RESULTS / "complete_eval_report.md"
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    (RESULTS / "complete_eval_report.json").write_text(
        json.dumps({"corpora": parts}, indent=2) + "\n", encoding="utf-8"
    )
    print(f"[report] combined -> {out}")


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    parts: list[dict] = []

    # --- Immediate reports from already-complete runs ---
    done = [
        (RESULTS / "run_20260718T182612Z_cooper_raw.json", "cooperbench_python_raw"),
        (RESULTS / "run_20260718T182612Z_cooper_structured.json", "cooperbench_python_structured"),
        (RESULTS / "run_20260718T224427Z.json", "hard_negatives_raw"),
        (RESULTS / "run_hard_negatives_structured_final.json", "hard_negatives_structured"),
    ]
    for path, name in done:
        if path.exists() and _n(path) > 0:
            parts.append(_score_simple(path, name))

    # Interim combined (will rewrite after live evals)
    _combined_report(parts)

    # --- Live evals (serialized) ---
    blind = ROOT / "data" / "pairs" / "blind_eval"
    twins = ROOT / "data" / "pairs" / "hard_compatible"

    blind_raw = _eval_raw(
        blind,
        RESULTS / "blind_raw_checkpoint.json",
        RESULTS / "eval_blind_raw_live.log",
        _expected(blind),
    )
    _score_blind(blind_raw)
    parts.append(_score_simple(blind_raw, "blind_eval_raw"))

    twins_raw = _eval_raw(
        twins,
        RESULTS / "twins_raw_checkpoint.json",
        RESULTS / "eval_twins_raw_live.log",
        _expected(twins),
    )
    parts.append(_score_simple(twins_raw, "hard_compatible_raw"))

    blind_struct = _eval_structured(
        blind,
        RESULTS / "blind_structured_checkpoint.json",
        RESULTS / "eval_blind_structured_live.log",
        _expected(blind),
    )
    parts.append(_score_simple(blind_struct, "blind_eval_structured"))

    twins_struct = _eval_structured(
        twins,
        RESULTS / "twins_structured_checkpoint.json",
        RESULTS / "eval_twins_structured_live.log",
        _expected(twins),
    )
    parts.append(_score_simple(twins_struct, "hard_compatible_structured"))

    # Publication-eval on blind (fair primary corpus) if both modes exist
    try:
        _run(
            [
                PY,
                "-m",
                "quorum",
                "publication-eval",
                "--cooper-raw",
                str(RESULTS / "run_20260718T182612Z_cooper_raw.json"),
                "--cooper-structured",
                str(RESULTS / "run_20260718T182612Z_cooper_structured.json"),
                "--hard-raw",
                str(blind_raw),
                "--hard-structured",
                str(blind_struct),
                "--pairs-dir",
                str(ROOT / "data" / "pairs"),
            ]
        )
    except Exception as exc:
        print(f"[warn] publication-eval failed: {exc}", flush=True)

    _combined_report(parts)
    print("Done. See results/complete_eval_report.md", flush=True)


if __name__ == "__main__":
    main()
