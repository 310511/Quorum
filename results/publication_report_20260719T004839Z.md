# Quorum Publication Evaluation

- Generated: `20260719T004839Z`
- Combined N: **116**
- Label distribution: `{'conflict': 109, 'no_conflict': 7}`

## Systems

- **A_baseline** — Single-model baseline
- **B_majority_vote** — Majority vote
- **C_legacy_escalation** — Current escalation policy
- **D_evidence_weighted_raw** — Evidence-weighted committee (raw)
- **E_evidence_weighted_structured** — Evidence-weighted + structured AST

## Main results (combined)

| System | Acc | Acc 95% CI | P | R | F1 | F1 95% CI | Coverage | Escalation | Latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A_baseline | 7.8% | [4.1%, 14.1%] | 60.0% | 5.5% | 10.1% | [3.5%, 17.7%] | 100.0% | 0.0% | 24.5s |
| B_majority_vote | 94.0% | [88.1%, 97.0%] | 94.0% | 100.0% | 96.9% | [94.1%, 98.7%] | 100.0% | 0.0% | 48.4s |
| C_legacy_escalation | 0.9% | [0.2%, 4.7%] | 100.0% | 100.0% | 100.0% | [100.0%, 100.0%] | 0.9% | 99.1% | 48.4s |
| D_evidence_weighted_raw | 7.8% | [4.1%, 14.1%] | 66.7% | 88.9% | 76.2% | [55.6%, 91.7%] | 12.1% | 87.9% | 48.4s |
| E_evidence_weighted_structured | 8.6% | [4.7%, 15.1%] | 62.5% | 100.0% | 76.9% | [76.9%, 76.9%] | 13.8% | 86.2% | 47.0s |

## McNemar paired significance

| Comparison | b01 | b10 | χ² | p-value |
|---|---:|---:|---:|---:|
| A_baseline_vs_B_majority_vote | 103 | 3 | 92.462 | 6.862e-22 |
| A_baseline_vs_C_legacy_escalation | 0 | 0 | 0.000 | 1 |
| A_baseline_vs_D_evidence_weighted_raw | 3 | 2 | 0.000 | 1 |
| A_baseline_vs_E_evidence_weighted_structured | 4 | 3 | 0.000 | 1 |
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
| model_reasoning_error | 100 |
| hallucinated_evidence | 14 |
| adjudication_error | 0 |
| dataset_ambiguity | 11 |

### Errors by system

- **A_baseline**: dataset_ambiguity=3, hallucinated_evidence=4, model_reasoning_error=100
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

## Corpus: hard_benchmark (N=100)

| System | Acc | P | R | F1 | Coverage | Escalation |
|---|---:|---:|---:|---:|---:|---:|
| A_baseline | 0.0% | 0.0% | 0.0% | 0.0% | 100.0% | 0.0% |
| B_majority_vote | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% |
| C_legacy_escalation | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 100.0% |
| D_evidence_weighted_raw | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 100.0% |
| E_evidence_weighted_structured | 1.0% | 100.0% | 100.0% | 100.0% | 1.0% | 99.0% |

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
- `hard_aliasing_contract_0004` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_aliasing_contract_0010` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_aliasing_contract_0016` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_aliasing_contract_0022` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_aliasing_contract_0028` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_aliasing_contract_0034` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_aliasing_contract_0040` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_aliasing_contract_0046` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_aliasing_contract_0052` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_aliasing_contract_0058` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_aliasing_contract_0064` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_aliasing_contract_0070` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_aliasing_contract_0076` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_aliasing_contract_0082` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_aliasing_contract_0088` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_aliasing_contract_0094` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_aliasing_contract_0100` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0001` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0007` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0013` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0019` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0025` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0031` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0037` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0043` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0049` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0055` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=conflict
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0061` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0067` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0073` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0079` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0085` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0091` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_boundary_contract_0097` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_case_sensitivity_0006` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_case_sensitivity_0012` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_case_sensitivity_0018` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_case_sensitivity_0024` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_case_sensitivity_0030` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_case_sensitivity_0036` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_case_sensitivity_0042` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_case_sensitivity_0048` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_case_sensitivity_0054` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_case_sensitivity_0060` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_case_sensitivity_0066` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_case_sensitivity_0072` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_case_sensitivity_0078` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_case_sensitivity_0084` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_case_sensitivity_0090` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_case_sensitivity_0096` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_error_contract_0005` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_error_contract_0011` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_error_contract_0017` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_error_contract_0023` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_error_contract_0029` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_error_contract_0035` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_error_contract_0041` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_error_contract_0047` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_error_contract_0053` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_error_contract_0059` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_error_contract_0065` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_error_contract_0071` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_error_contract_0077` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_error_contract_0083` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_error_contract_0089` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_error_contract_0095` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0002` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0008` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0014` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0020` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0026` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0032` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0038` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0044` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0050` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0056` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0062` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0068` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0074` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0080` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0086` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0092` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_ordering_default_0098` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0003` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0009` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0015` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0021` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0027` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0033` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0039` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0045` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0051` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0057` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0063` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0069` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0075` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0081` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0087` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0093` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
- `hard_sentinel_default_0099` truth=conflict A=no_conflict B=conflict C=escalate D=escalate E=escalate
  - error/A_baseline: no_conflict → model_reasoning_error
