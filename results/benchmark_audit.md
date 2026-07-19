# Benchmark Audit — hard_benchmark (raw)

Source run: `run_20260718T225424Z.json`
N = 130 (100 conflict + 30 compatible)

## Headline

- Baseline accuracy: **130/130 (100%)**
- Committee accuracy: **102/130 (78.5%)** (1 escalate)

## PART 1 — How the baseline decides

The baseline is **not** a handcrafted heuristic engine.
It is a **single LLM call** (`deepseek-coder:6.7b`) using the same `build_prompt(pair)` as every committee member (`quorum/baseline.py`).

Decision path:
1. `load_pair` reads `branch_a.diff`, `branch_b.diff`, and `context.md`
2. Prompt includes the full context block
3. Model returns JSON `{verdict, confidence, reasoning, evidence}`
4. Verdict is normalized (`compatible` → `no_conflict`)

### Privileged information

YES. `context.md` always contains:
- `Ground truth: conflict|no_conflict`
- `Conflict type: ...`
- Notes describing the exact bug
- `Validation: ... merged tests fail/pass`

This is unavailable in a realistic merge review, and is **not** withheld from the committee (committee receives the identical prompt). The baseline advantage is that a single stronger/coding model more reliably *obeys* the leaked validation line, while the committee often outvotes it on compatible examples.

### Per-example baseline table

- Correct: 130/130
- Mean confidence (reported): 1.000
- Explicit validation citations: 20/130

Full per-example records: `results/baseline_per_example.json`

Sample (first 5 + first 3 compatible):

- `hard_000_profile_rename_stale` gt=`conflict` pred=`conflict` conf=1.0 rules=['semantic_diff_reasoning_or_implicit_leak'] evidence=['The test cases in Branch B fail because they expect compute_profile_total while the merged codebase calls compute_profile_total_v2.']
- `hard_001_metrics_signature_break` gt=`conflict` pred=`conflict` conf=1.0 rules=['semantic_diff_reasoning_or_implicit_leak'] evidence=['Branch A modifies `build_metrics_payload` with keyword-only arguments, but Branch B calls this function using positional arguments.']
- `hard_002_checkout_import_drift` gt=`conflict` pred=`conflict` conf=1.0 rules=['semantic_diff_reasoning_or_implicit_leak'] evidence=['The diff of Branch A shows that it moves the function definition from `checkout_utils.py` to `checkout_tokens.py`', 'The diff of Branch B still imports the function from its original location (`checkout_utils.py`)', 'Running tests in Branch B fails because it expects `normalize_checkout_token` to be defined in `checkout_utils.py`']
- `hard_003_cache_return_contract` gt=`conflict` pred=`conflict` conf=1.0 rules=['cited_conflict_type:return_contract'] evidence=["The diffs show that Branch A changes the return contract of fetch_cache_record and Branch B adds a new function score_for which uses the same item_id as fetch_cache_record but accesses 'score' from the returned payload instead of directly."]
- `hard_004_ledger_exception_contract` gt=`conflict` pred=`conflict` conf=1.0 rules=['semantic_diff_reasoning_or_implicit_leak'] evidence=["Branch A modifies an exception class (LedgerError -> LedgerGone) used in Branch B's tests."]
- `hard_10000_profile_ok0_compatible` gt=`no_conflict` pred=`no_conflict` conf=1.0 rules=['cited_context_validation_line'] evidence=['Branch A and Branch B have no overlapping lines of code', 'Validation: Branch A tests pass, Branch B tests pass, merged tests pass']
- `hard_10001_metrics_ok1_compatible` gt=`no_conflict` pred=`no_conflict` conf=1.0 rules=['semantic_diff_reasoning_or_implicit_leak'] evidence=['Branch A and Branch B have no overlapping lines of code', "Both Branch A and Branch B's functionalities are entirely new to the system"]
- `hard_10002_checkout_ok2_compatible` gt=`no_conflict` pred=`no_conflict` conf=1.0 rules=['cited_context_validation_line'] evidence=['Branch A and Branch B each have their own tests that pass independently', 'Validation: Merged tests pass']

## PART 5 — Confusion matrices

### Baseline

|  | Pred conflict | Pred no_conflict/other |
|---|---:|---:|
| **Truth conflict** | TP=100 | FN=0 |
| **Truth no_conflict** | FP=0 | TN=30 |

- Sensitivity: 1.000  Specificity: 1.000  Balanced Acc: 1.000  MCC: 1.000  Accuracy: 1.000

### Majority

|  | Pred conflict | Pred no_conflict/other |
|---|---:|---:|
| **Truth conflict** | TP=100 | FN=0 |
| **Truth no_conflict** | FP=27 | TN=3 |

- Sensitivity: 1.000  Specificity: 0.100  Balanced Acc: 0.550  MCC: 0.281  Accuracy: 0.792

### Evidence-weighted committee

|  | Pred conflict | Pred no_conflict/other |
|---|---:|---:|
| **Truth conflict** | TP=100 | FN=0 |
| **Truth no_conflict** | FP=28 | TN=2 |

- Sensitivity: 1.000  Specificity: 0.067  Balanced Acc: 0.533  MCC: 0.228  Accuracy: 0.785

## PART 7 — Blind human-style review (n=20)

Agreement with labels: **20/20 = 100%** (seed=42)

Method: diffs only; no `label.json`; no ground-truth lines from context.

### `hard_028_parser_1_exception_contract`
- Blind: **Conflict** — Contract/signature/exception/default semantics drift signals
- Label (revealed after): **Conflict**
- Agree: True

### `hard_006_warehouse_rename_stale`
- Blind: **Conflict** — Rename/removal with likely stale reference across branches
- Label (revealed after): **Conflict**
- Agree: True

### `hard_070_payments_3_exception_contract`
- Blind: **Conflict** — Contract/signature/exception/default semantics drift signals
- Label (revealed after): **Conflict**
- Agree: True

### `hard_062_checkout_3_import_drift`
- Blind: **Conflict** — Rename/removal with likely stale reference across branches
- Label (revealed after): **Conflict**
- Agree: True

### `hard_057_notifier_2_return_contract`
- Blind: **Conflict** — Contract/signature/exception/default semantics drift signals
- Label (revealed after): **Conflict**
- Agree: True

### `hard_035_tickets_1_default_semantics`
- Blind: **Conflict** — Contract/signature/exception/default semantics drift signals
- Label (revealed after): **Conflict**
- Agree: True

### `hard_026_warehouse_1_import_drift`
- Blind: **Conflict** — Rename/removal with likely stale reference across branches
- Label (revealed after): **Conflict**
- Agree: True

### `hard_022_checkout_1_exception_contract`
- Blind: **Conflict** — Contract/signature/exception/default semantics drift signals
- Label (revealed after): **Conflict**
- Agree: True

### `hard_10008_parser_ok8_compatible`
- Blind: **Compatible** — Disjoint new modules with no removed symbols
- Label (revealed after): **Compatible**
- Agree: True

### `hard_008_parser_import_drift`
- Blind: **Conflict** — Rename/removal with likely stale reference across branches
- Label (revealed after): **Conflict**
- Agree: True

### `hard_007_search_signature_break`
- Blind: **Conflict** — Rename/removal with likely stale reference across branches
- Label (revealed after): **Conflict**
- Agree: True

### `hard_023_cache_1_default_semantics`
- Blind: **Conflict** — Contract/signature/exception/default semantics drift signals
- Label (revealed after): **Conflict**
- Agree: True

### `hard_055_tickets_2_signature_break`
- Blind: **Conflict** — Rename/removal with likely stale reference across branches
- Label (revealed after): **Conflict**
- Agree: True

### `hard_059_auth_2_default_semantics`
- Blind: **Conflict** — Contract/signature/exception/default semantics drift signals
- Label (revealed after): **Conflict**
- Agree: True

### `hard_10029_pricing_ok29_compatible`
- Blind: **Compatible** — Disjoint new modules with no removed symbols
- Label (revealed after): **Compatible**
- Agree: True

### `hard_050_payments_2_import_drift`
- Blind: **Conflict** — Rename/removal with likely stale reference across branches
- Label (revealed after): **Conflict**
- Agree: True

### `hard_10007_search_ok7_compatible`
- Blind: **Compatible** — Disjoint new modules with no removed symbols
- Label (revealed after): **Compatible**
- Agree: True

### `hard_056_scheduler_2_import_drift`
- Blind: **Conflict** — Rename/removal with likely stale reference across branches
- Label (revealed after): **Conflict**
- Agree: True

### `hard_10014_inventory_ok14_compatible`
- Blind: **Compatible** — Disjoint new modules with no removed symbols
- Label (revealed after): **Compatible**
- Agree: True

### `hard_071_catalog_3_default_semantics`
- Blind: **Conflict** — Contract/signature/exception/default semantics drift signals
- Label (revealed after): **Conflict**
- Agree: True

