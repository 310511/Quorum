# Quorum publication evaluation guide

## Corpora

| Corpus | Size | Notes |
|--------|------|-------|
| CooperBench Python | 16 | Real multi-repo merge pairs (9 conflict / 7 compatible) |
| Hard semantic benchmark | 130 | 100 verified conflicts + 30 compatible controls |

Hard pairs are self-contained mini-repos. Each conflict example satisfies:

1. Branch A compiles and all tests pass
2. Branch B compiles and all tests pass
3. Merged tree compiles but tests fail (semantic inconsistency)

## Systems compared

| ID | System |
|----|--------|
| A | Single-model baseline (`deepseek-coder:6.7b`) |
| B | Majority vote over the three-model committee |
| C | Legacy escalation policy (any disagreement → escalate) |
| D | Evidence-weighted committee on raw diffs |
| E | Evidence-weighted committee on structured AST |

## Statistics

- Accuracy / Precision / Recall / F1 / Coverage / Escalation rate / mean latency
- 95% Wilson score intervals for Acc/P/R; bootstrap percentile CI for F1
- McNemar mid-p / continuity-corrected χ² on paired correctness (decided predictions)

## Error taxonomy

Every incorrect *decided* prediction is labeled with exactly one primary cause:

1. **dataset_ambiguity** — models unanimously disagree with the gold label
2. **hallucinated_evidence** — cited identifiers absent from the change
3. **representation_error** — raw vs structured disagree and only one is correct
4. **adjudication_error** — majority vote correct but committee policy wrong
5. **model_reasoning_error** — residual reasoning failure

## Reproducing the paper tables

```bash
# 1. Ensure CooperBench raw+structured runs exist
python -m quorum eval-cooperbench data/pairs

# 2. Generate hard benchmark (already done if data/pairs/hard_benchmark exists)
python -m quorum generate-hard-benchmark --conflicts 100 --compatible 30

# 3. Evaluate hard benchmark (hours; checkpointed)
python -m quorum --config config_hard.yaml eval data/pairs/hard_benchmark --input-mode raw --checkpoint results/hard_raw_checkpoint.json
python -m quorum --config config_hard.yaml eval data/pairs/hard_benchmark --input-mode structured --checkpoint results/hard_structured_checkpoint.json

# 4. Build publication package
python -m quorum publication-eval --cooper-raw ... --cooper-structured ... --hard-raw ... --hard-structured ...
```
