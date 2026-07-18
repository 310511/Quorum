"""Import CooperBench merge pair snapshots into Quorum data/pairs format."""

from __future__ import annotations

import difflib
import json
import shutil
import zipfile
from pathlib import Path

GROUND_TRUTH = {
    "conflict": "conflict",
    "clean_merge": "compatible",
}


def _collect_rel_paths(root: Path) -> set[str]:
    root = Path(root)
    if not root.is_dir():
        return set()
    return {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and not p.name.startswith(".")
    }


def _infer_language(meta: dict) -> str:
    exts = set()
    for rel in meta.get("files_touched", []):
        if "." in rel:
            exts.add(rel.rsplit(".", 1)[-1].lower())
    mapping = {
        "py": "python",
        "go": "go",
        "ts": "typescript",
        "tsx": "typescript",
        "rs": "rust",
    }
    for ext in exts:
        if ext in mapping:
            return mapping[ext]
    return "unknown"


def _file_lines(path: Path | None) -> list[str]:
    if path is None or not path.exists():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)


def _branch_diff(merge_base_dir: Path, branch_dir: Path, rel_paths: set[str]) -> str:
    chunks: list[str] = []
    for rel in sorted(rel_paths):
        base_path = merge_base_dir / rel
        branch_path = branch_dir / rel
        base_lines = _file_lines(base_path if base_path.exists() else None)
        branch_lines = _file_lines(branch_path if branch_path.exists() else None)
        if base_lines == branch_lines:
            continue
        diff = difflib.unified_diff(
            base_lines,
            branch_lines,
            fromfile=f"a/{rel}",
            tofile=f"b/{rel}",
        )
        block = "".join(diff)
        if block:
            chunks.append(block)
    return "\n".join(chunks).strip()


def _context_md(meta: dict, feature_a: str, feature_b: str) -> str:
    fa = meta.get("feature_a", {})
    fb = meta.get("feature_b", {})
    files = ", ".join(meta.get("files_touched", []))
    return f"""# CooperBench pair: {meta.get("pair_id")}

- **Repo:** {meta.get("github")}
- **Base commit:** {meta.get("base_commit")}
- **CooperBench label:** {meta.get("label")}

## Feature A (branch_a): {fa.get("title", "")}

{feature_a.strip()}

## Feature B (branch_b): {fb.get("title", "")}

{feature_b.strip()}

## Files touched
{files}
"""


def _label_json(meta: dict, language: str) -> dict:
    label = meta.get("label", "")
    if label not in GROUND_TRUTH:
        raise ValueError(f"unknown CooperBench label: {label!r}")
    fa = meta.get("feature_a", {})
    fb = meta.get("feature_b", {})
    return {
        "ground_truth": GROUND_TRUTH[label],
        "language": language,
        "source": "CooperBench",
        "repo": meta.get("github"),
        "pair_id": meta.get("pair_id"),
        "cooperbench_label": label,
        "notes": f"{fa.get('title', 'feature A')} vs {fb.get('title', 'feature B')}",
    }


def import_pair_from_dir(src: Path, dest: Path) -> None:
    src = Path(src)
    dest = Path(dest)
    meta = json.loads((src / "meta.json").read_text(encoding="utf-8"))
    language = _infer_language(meta)

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    for sub in ("merge_base", "branch_a", "branch_b"):
        shutil.copytree(src / sub, dest / sub)

    merge_base_dir = dest / "merge_base"
    branch_a_dir = dest / "branch_a"
    branch_b_dir = dest / "branch_b"
    rel_paths = _collect_rel_paths(merge_base_dir) | _collect_rel_paths(branch_a_dir) | _collect_rel_paths(branch_b_dir)

    (dest / "branch_a.diff").write_text(
        _branch_diff(merge_base_dir, branch_a_dir, rel_paths), encoding="utf-8"
    )
    (dest / "branch_b.diff").write_text(
        _branch_diff(merge_base_dir, branch_b_dir, rel_paths), encoding="utf-8"
    )

    feature_a = (src / "feature_a.md").read_text(encoding="utf-8") if (src / "feature_a.md").exists() else ""
    feature_b = (src / "feature_b.md").read_text(encoding="utf-8") if (src / "feature_b.md").exists() else ""
    (dest / "context.md").write_text(_context_md(meta, feature_a, feature_b), encoding="utf-8")
    (dest / "label.json").write_text(
        json.dumps(_label_json(meta, language), indent=2) + "\n", encoding="utf-8"
    )
    shutil.copy2(src / "meta.json", dest / "meta.json")


def import_cooperbench_zip(
    zip_path: Path,
    dest_dir: Path,
    *,
    skip_existing: bool = False,
) -> list[str]:
    zip_path = Path(zip_path)
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    imported: list[str] = []

    with zipfile.ZipFile(zip_path) as zf:
        pair_roots = sorted(
            {name.split("/")[0] for name in zf.namelist() if name.endswith("/meta.json")}
        )
        for pair_id in pair_roots:
            dest = dest_dir / pair_id
            if skip_existing and dest.exists():
                continue
            tmp = dest_dir / f".import_tmp_{pair_id}"
            if tmp.exists():
                shutil.rmtree(tmp)
            tmp.mkdir(parents=True)
            for member in zf.namelist():
                if member.startswith(f"{pair_id}/") and not member.endswith("/"):
                    target = tmp / member[len(pair_id) + 1 :]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(zf.read(member))
            import_pair_from_dir(tmp, dest)
            shutil.rmtree(tmp)
            imported.append(pair_id)

    return imported
