# Real-World Semantic Merge Dataset — Full Protocol

## Overview

This pipeline builds a **real-world** benchmark for semantic merge conflict detection from git merge history. It is separate from CooperBench imports and synthetic hard benchmarks.

## Phase map

| Phase | Command | Output |
|-------|---------|--------|
| 1 Mine | `real-world-pipeline mine` | `dataset/real_world/merges.jsonl` |
| 2 Filter | `real-world-pipeline filter` | `dataset/real_world/filtered.jsonl` |
| 3 Detect | `real-world-pipeline detect` | `dataset/real_world/candidates.jsonl` |
| 4 Classify | `real-world-pipeline classify` | `dataset/real_world/classified.jsonl` |
| 5 Package | `real-world-pipeline packages` | `dataset/real_world_candidates/<id>/` |
| 6 Heuristics | `real-world-pipeline heuristics` | `dataset/real_world/heuristics.jsonl` |
| 7 Queue | `real-world-pipeline queue` | `dataset/real_world/review_queue.csv` |
| 7b Materialize | `real-world-pipeline materialize` | `dataset/real_world/examples/` (Quorum layout) |
| 8 Annotate | `real-world-pipeline serve` | `annotations.jsonl`, `reviewer_*.jsonl` |
| 9 Agreement | `real-world-pipeline agreement` | `agreement_report.md` |
| 10 Freeze | `real-world-pipeline freeze` | `dataset/real_world/examples/` |

All phases support **resume** via JSONL append (except `--rebuild`).

## Candidate package schema

Each `dataset/real_world_candidates/<id>/` contains:

- `metadata.json` — SHAs, files, category, heuristic estimate
- `base/` — merge-base Python sources
- `left.diff` — branch A vs merge-base
- `right.diff` — branch B vs merge-base
- `changed_symbols.json` — AST-derived symbol deltas
- `summary.md` — human-readable overview

## Annotation protocol

1. Open review UI with distinct reviewer IDs (`?reviewer=A`, `?reviewer=B`)
2. For each example, read both diffs and changed symbols
3. Label **Conflict** if merged semantics would break callers/tests/contracts
4. Label **Compatible** if branches compose safely despite overlapping files
5. **Skip** ambiguous cases — do not guess
6. Write a short rationale (required for publication)

Heuristic `estimated_label` is a **prior only**, never ground truth.

## Semantic categories

API change, Function signature, Default parameter, Return value, Exception contract, State mutation, Ownership, Validation, ORM, Transaction, Dependency Injection, Routing, Middleware, Async, Inheritance, Caching, Resource lifetime, DataFrame semantics, Serialization, Other.

## Reaching 200–250 examples

1. Mine all six repos (no `--limit`) or use `--since 2019-01-01` for tractability
2. Run phases 2–7; inspect `review_queue.csv` sorted by confidence
3. Annotate top candidates first; aim for balance across repos and categories
4. Run agreement; resolve disagreements in a third review pass
5. Freeze with `--require-agreement` for high-confidence subset

## Evaluating with Quorum

Export candidates first (creates `branch_a/`, `branch_b/`, `merge_base/`, diffs):

```bash
real-world-pipeline materialize
python -m quorum eval dataset/real_world/examples --input-mode structured
```

Examples without human labels have `"ground_truth": null` — eval runs but skips accuracy scoring.
