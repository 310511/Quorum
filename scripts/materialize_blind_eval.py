"""Materialize the blind_eval pack into runnable, leakage-free Quorum pairs.

Source (model-visible, opaque IDs):
    dataset/blind_eval/pairs/<id>/{left.diff,right.diff,base/,meta.json}
Sealed (scoring only, NOT shown to models):
    dataset/blind_eval/labels.sealed.jsonl

Output pairs land in data/pairs/blind_eval/<id>/ with:
    branch_a.diff, branch_b.diff        (from left/right diffs)
    merge_base/, branch_a/, branch_b/   (trees for structured AST delta)
    label.json                          (ground_truth only; never prompted)

No context.md is written, so build_prompt() sees no privileged text -> blind.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "dataset" / "blind_eval"
PAIRS_SRC = SRC / "pairs"
SEALED = SRC / "labels.sealed.jsonl"
DEST = ROOT / "data" / "pairs" / "blind_eval"


def _sealed_labels() -> dict[str, str]:
    labels: dict[str, str] = {}
    for line in SEALED.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        outcome = str(row.get("outcome") or "").lower()
        gt = "conflict" if outcome == "conflict" else "no_conflict"
        labels[str(row["pair_id"])] = gt
    return labels


def _apply(tree: Path, patch: str) -> None:
    normalized = patch if patch.endswith("\n") else patch + "\n"
    result = subprocess.run(
        ["git", "apply", "--whitespace=nowarn", "-"],
        cwd=tree,
        input=normalized.encode("utf-8"),
        capture_output=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).decode("utf-8", errors="replace")
        raise RuntimeError(f"git apply failed in {tree}: {detail}")


def _copy_base(base_src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(
        base_src,
        dest,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
    )


def materialize() -> list[str]:
    labels = _sealed_labels()
    DEST.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    skipped: list[tuple[str, str]] = []

    for pdir in sorted(PAIRS_SRC.iterdir()):
        if not pdir.is_dir():
            continue
        pid = pdir.name
        left = (pdir / "left.diff").read_text(encoding="utf-8")
        right = (pdir / "right.diff").read_text(encoding="utf-8")
        base_src = pdir / "base"
        gt = labels.get(pid)
        if gt is None:
            skipped.append((pid, "no_sealed_label"))
            continue

        out = DEST / pid
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)

        _copy_base(base_src, out / "merge_base")
        (out / "branch_a.diff").write_text(
            left.rstrip() + "\n", encoding="utf-8"
        )
        (out / "branch_b.diff").write_text(
            right.rstrip() + "\n", encoding="utf-8"
        )

        try:
            _copy_base(base_src, out / "branch_a")
            _apply(out / "branch_a", left)
            _copy_base(base_src, out / "branch_b")
            _apply(out / "branch_b", right)
        except RuntimeError as exc:
            shutil.rmtree(out)
            skipped.append((pid, str(exc)[:80]))
            continue

        # label.json is read only for scoring; build_prompt() never sees it.
        (out / "label.json").write_text(
            json.dumps(
                {
                    "ground_truth": gt,
                    "language": "python",
                    "source": "blind_eval",
                    "pair_id": pid,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        created.append(pid)

    print(f"Materialized {len(created)} blind pairs into {DEST}")
    if skipped:
        print(f"Skipped {len(skipped)}:")
        for pid, why in skipped[:20]:
            print(f"  - {pid}: {why}")
    return created


if __name__ == "__main__":
    materialize()
