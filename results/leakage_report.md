# Leakage Report — hard_benchmark

## Executive finding

**Critical label leakage.** Every prompt includes `context.md`, and every `context.md` contains an explicit `Ground truth:` line plus a validation sentence stating whether merged tests pass or fail.

## Perfect predictors (no semantic reasoning required)

- **filename_contains_compatible**: accuracy=1.000 — If name contains '_compatible' predict no_conflict else conflict
- **context_md_ground_truth_line**: accuracy=1.000 — Parse 'Ground truth: `...`' from context.md (fed into every prompt)
- **context_merged_tests_outcome**: accuracy=1.000 — Parse validation sentence about merged tests pass/fail
- **filename_mutation_suffix**: accuracy=1.000 — Conflict-type suffix vs _compatible in directory name

## Prompt construction

- `load_pair()` reads `context.md` into `BranchPair.context`
- `build_prompt()` inserts it under `## Merge-base context` (raw + structured)
- Baseline and all committee models receive the **same** leaked prompt
- `label.json` / `meta.json` are **not** inserted into the prompt (but their contents are duplicated into `context.md`)

## Filename leakage

- Conflict pairs encode mutation type: `rename_stale`, `signature_break`, etc.
- Compatible pairs include `_compatible` (and often `okN`)
- Filenames are **not** currently placed in the prompt body

## Diff comment leakage

Generated diffs often contain instructive comments such as `# Relies on old positional/default signature`, `# New contract`, `# Depends on historical default of 10`, `# Moved to ...`.

## Baseline citation behavior

- Baseline rows citing validation line/paraphrase: 20/130
- Citation counter: {"semantic_diff_reasoning_or_implicit_leak": 102, "cited_conflict_type": 8, "cited_context_validation_line": 16, "cited_validation_paraphrase": 4}
- Pairs where a committee model literally said 'ground truth': 23

## Contrast: hard_negatives (records1)

Imported `hard_negatives` contexts do **not** contain `Ground truth:` lines. They include family/intent/hidden-invariant text which is descriptive but does not emit the binary label.

