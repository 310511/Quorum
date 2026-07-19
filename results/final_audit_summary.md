# Final Audit Summary

## Answers

### 1. Is the benchmark fair?
**No** — not in its current evaluation configuration. Prompts include explicit labels.

### 2. Is the baseline realistic?
**Partially.** Architecturally it is a realistic single-model baseline, but its 100% score is **not** a realistic measure of semantic-conflict skill because of label leakage in `context.md`. It is not a handcrafted rule oracle.

### 3. Does the committee have access to the same information?
**Yes.** Identical `build_prompt()` output. The committee's lower accuracy on compatible pairs is mostly false-positive reasoning, sometimes *despite* the leak.

### 4. Is there benchmark leakage?
**Yes — severe.** Perfect predictors from context ground-truth / merged-test validation / filenames all achieve ~100%. See `leakage_report.md`.

### 5. Is the benchmark difficult enough for publication?
**Not as currently generated.** Difficulty distribution is Easy/Medium template mutations; no true hidden-invariant Hard cases in `hard_benchmark`. `records1.json` / `hard_negatives` are closer to publication-grade Hard.

### 6. Should any benchmark examples be removed?
Remove or rewrite all prompts' leaked context. Compatible controls can stay if labels are withheld; conflict templates are fine for unit tests but weak as a solo publication corpus. Prefer replacing synthetic `hard_benchmark` eval with `hard_negatives` (records1) once labels are scrubbed from any residual context.

### 7. Should the benchmark be regenerated?
**Evaluation packaging must be fixed** (strip Ground truth / validation outcomes from prompted context). Full regeneration of synthetic templates is optional; regeneration is recommended if publication claims 'hard semantic conflicts' — use records1-style oracles instead of rename/signature toys.

## Root cause of 130/130 vs 78.5%

1. Every prompt includes `context.md` with `Ground truth:` and `merged tests fail/pass` (severe leakage).
2. Baseline (single deepseek) is 130/130 — not via handcrafted heuristics, but by using that privileged context (explicit validation citations on 20/130, especially compatible controls).
3. Committee receives the **same** leaked prompt, yet on compatible pairs 2/3 models often invent false conflicts; evidence-weighted adjudication then yields 27–28 false positives → **78.5%**.
4. Conflict pairs are Easy/Medium templates, so both systems are near-ceiling there (100/100 TP).

## Human review note

Blind mechanical review of 20 diffs agreed with labels **20/20**. That is itself an audit finding: generator patterns (disjoint alpha/beta modules vs rename/signature/contract templates) are detectable without LLM reasoning.

## Metrics snapshot

- **Baseline**: Acc=1.000 BalAcc=1.000 MCC=1.000 (TP=100 FP=0 TN=30 FN=0)
- **Majority**: Acc=0.792 BalAcc=0.550 MCC=0.281 (TP=100 FP=27 TN=3 FN=0)
- **Evidence-weighted committee**: Acc=0.785 BalAcc=0.533 MCC=0.228 (TP=100 FP=28 TN=2 FN=0)

## Deliverables

- `results/benchmark_audit.md`
- `results/leakage_report.md`
- `results/difficulty_distribution.json`
- `results/compatible_error_analysis.md`
- `results/oracle_check.json`
- `results/final_audit_summary.md`
- `results/human_review_sample.json` (supporting)

