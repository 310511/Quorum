# Quorum Publication Evaluation

- Generated: `20260718T202316Z`
- Combined N: **16**
- Label distribution: `{'conflict': 9, 'no_conflict': 7}`

## Systems

- **A_baseline** — Single-model baseline
- **B_majority_vote** — Majority vote
- **C_legacy_escalation** — Current escalation policy
- **D_evidence_weighted_raw** — Evidence-weighted committee (raw)
- **E_evidence_weighted_structured** — Evidence-weighted + structured AST

## Main results (combined)

| System | Acc | Acc 95% CI | P | R | F1 | F1 95% CI | Coverage | Escalation | Latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A_baseline | 56.2% | [33.2%, 76.9%] | 60.0% | 66.7% | 63.2% | [37.5%, 81.8%] | 100.0% | 0.0% | 22.6s |
| B_majority_vote | 56.2% | [33.2%, 76.9%] | 56.2% | 100.0% | 72.0% | [72.0%, 72.0%] | 100.0% | 0.0% | 58.8s |
| C_legacy_escalation | 6.2% | [1.1%, 28.3%] | 100.0% | 100.0% | 100.0% | [100.0%, 100.0%] | 6.2% | 93.8% | 58.8s |
| D_evidence_weighted_raw | 56.2% | [33.2%, 76.9%] | 66.7% | 88.9% | 76.2% | [55.6%, 91.7%] | 87.5% | 12.5% | 58.8s |
| E_evidence_weighted_structured | 56.2% | [33.2%, 76.9%] | 60.0% | 100.0% | 75.0% | [57.1%, 88.9%] | 93.8% | 6.2% | 53.6s |

## McNemar paired significance

| Comparison | b01 | b10 | χ² | p-value |
|---|---:|---:|---:|---:|
| A_baseline_vs_B_majority_vote | 3 | 3 | 0.167 | 0.6831 |
| A_baseline_vs_C_legacy_escalation | 0 | 0 | 0.000 | 1 |
| A_baseline_vs_D_evidence_weighted_raw | 3 | 2 | 0.000 | 1 |
| A_baseline_vs_E_evidence_weighted_structured | 3 | 3 | 0.167 | 0.6831 |
| B_majority_vote_vs_C_legacy_escalation | 0 | 0 | 0.000 | 1 |
| B_majority_vote_vs_D_evidence_weighted_raw | 1 | 1 | 0.500 | 0.4795 |
| B_majority_vote_vs_E_evidence_weighted_structured | 0 | 0 | 0.000 | 1 |
| C_legacy_escalation_vs_D_evidence_weighted_raw | 0 | 0 | 0.000 | 1 |
| C_legacy_escalation_vs_E_evidence_weighted_structured | 0 | 0 | 0.000 | 1 |
| D_evidence_weighted_raw_vs_E_evidence_weighted_structured | 1 | 1 | 0.500 | 0.4795 |

## Error analysis

| Category | Count |
|---|---:|
| representation_error | 0 |
| model_reasoning_error | 0 |
| hallucinated_evidence | 14 |
| adjudication_error | 0 |
| dataset_ambiguity | 11 |

### Errors by system

- **A_baseline**: dataset_ambiguity=3, hallucinated_evidence=4
- **B_majority_vote**: dataset_ambiguity=3, hallucinated_evidence=4
- **D_evidence_weighted_raw**: dataset_ambiguity=3, hallucinated_evidence=2
- **E_evidence_weighted_structured**: dataset_ambiguity=2, hallucinated_evidence=4

## Corpus: cooperbench_python (N=16)

| System | Acc | P | R | F1 | Coverage | Escalation |
|---|---:|---:|---:|---:|---:|---:|
| A_baseline | 56.2% | 60.0% | 66.7% | 63.2% | 100.0% | 0.0% |
| B_majority_vote | 56.2% | 56.2% | 100.0% | 72.0% | 100.0% | 0.0% |
| C_legacy_escalation | 6.2% | 100.0% | 100.0% | 100.0% | 6.2% | 93.8% |
| D_evidence_weighted_raw | 56.2% | 66.7% | 88.9% | 76.2% | 87.5% | 12.5% |
| E_evidence_weighted_structured | 56.2% | 60.0% | 100.0% | 75.0% | 93.8% | 6.2% |

## Per-pair decision log (abbreviated)

- `pair_01_dottxt_ai_outlines_t1655_f9v10` truth=conflict A=conflict B=conflict C=escalate D=conflict E=conflict
- `pair_02_dottxt_ai_outlines_t1655_f3v9` truth=no_conflict A=conflict B=conflict C=escalate D=conflict E=escalate
  - error/A_baseline: conflict → dataset_ambiguity
  - error/B_majority_vote: conflict → dataset_ambiguity
  - error/D_evidence_weighted_raw: conflict → dataset_ambiguity
- `pair_03_dspy_t8587_f3v5` truth=conflict A=conflict B=conflict C=escalate D=conflict E=conflict
- `pair_04_dspy_t8563_f1v2` truth=no_conflict A=conflict B=conflict C=escalate D=conflict E=conflict
  - error/A_baseline: conflict → dataset_ambiguity
  - error/B_majority_vote: conflict → dataset_ambiguity
  - error/D_evidence_weighted_raw: conflict → dataset_ambiguity
  - error/E_evidence_weighted_structured: conflict → dataset_ambiguity
- `pair_07_huggingface_datasets_t6252_f3v5` truth=conflict A=no_conflict B=conflict C=escalate D=conflict E=conflict
  - error/A_baseline: no_conflict → hallucinated_evidence
- `pair_08_huggingface_datasets_t6252_f1v3` truth=no_conflict A=no_conflict B=conflict C=escalate D=conflict E=conflict
  - error/B_majority_vote: conflict → hallucinated_evidence
  - error/D_evidence_weighted_raw: conflict → hallucinated_evidence
  - error/E_evidence_weighted_structured: conflict → hallucinated_evidence
- `pair_09_llama_index_t18813_f1v3` truth=conflict A=no_conflict B=conflict C=escalate D=conflict E=conflict
  - error/A_baseline: no_conflict → hallucinated_evidence
- `pair_10_llama_index_t17244_f3v4` truth=no_conflict A=no_conflict B=conflict C=escalate D=no_conflict E=conflict
  - error/B_majority_vote: conflict → hallucinated_evidence
  - error/E_evidence_weighted_structured: conflict → hallucinated_evidence
- `pair_11_openai_tiktoken_t0_f1v3` truth=conflict A=no_conflict B=conflict C=escalate D=conflict E=conflict
  - error/A_baseline: no_conflict → hallucinated_evidence
- `pair_12_pallets_click_t2068_f2v4` truth=conflict A=conflict B=conflict C=escalate D=conflict E=conflict
- `pair_13_pallets_click_t2956_f3v8` truth=no_conflict A=conflict B=conflict C=escalate D=conflict E=conflict
  - error/A_baseline: conflict → dataset_ambiguity
  - error/B_majority_vote: conflict → dataset_ambiguity
  - error/D_evidence_weighted_raw: conflict → dataset_ambiguity
  - error/E_evidence_weighted_structured: conflict → dataset_ambiguity
- `pair_14_pallets_jinja_t1621_f1v6` truth=conflict A=conflict B=conflict C=escalate D=no_conflict E=conflict
  - error/D_evidence_weighted_raw: no_conflict → hallucinated_evidence
- `pair_15_pallets_jinja_t1559_f2v7` truth=no_conflict A=conflict B=conflict C=escalate D=escalate E=conflict
  - error/A_baseline: conflict → hallucinated_evidence
  - error/B_majority_vote: conflict → hallucinated_evidence
  - error/E_evidence_weighted_structured: conflict → hallucinated_evidence
- `pair_16_pillow_t290_f1v5` truth=conflict A=conflict B=conflict C=conflict D=conflict E=conflict
- `pair_17_pillow_t25_f1v5` truth=no_conflict A=no_conflict B=conflict C=escalate D=escalate E=conflict
  - error/B_majority_vote: conflict → hallucinated_evidence
  - error/E_evidence_weighted_structured: conflict → hallucinated_evidence
- `pair_19_samuelcolvin_dirty_equals_t43_f1v3` truth=conflict A=conflict B=conflict C=escalate D=conflict E=conflict
