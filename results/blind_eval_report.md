# Blind Evaluation Report

- Run: `run_blind_eval_raw_final.json` (raw, leakage-free)
- Scored: **200** pairs · balance {'no_conflict': 100, 'conflict': 100}
- Prompts contain no `context.md`, no ground-truth, no filenames with labels.

## Systems (conflict = positive)

| System | Acc | Prec | Recall | Spec | F1 | BalAcc | MCC | Cov | Esc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline (single LLM) | 50.0% | 0.0% | 0.0% | 100.0% | 0.0% | 50.0% | 0.00 | 100.0% | 0.0% |
| Majority vote | 50.0% | 50.0% | 100.0% | 0.0% | 66.7% | 50.0% | 0.00 | 100.0% | 0.0% |
| Evidence-weighted committee | 44.0% | 46.8% | 88.0% | 0.0% | 61.1% | 44.0% | -0.25 | 95.5% | 4.5% |

## Confusion matrices

### Baseline (single LLM)

|  | Pred conflict | Pred no_conflict/esc |
|---|---:|---:|
| **Truth conflict** | TP=0 | FN=100 |
| **Truth no_conflict** | FP=0 | TN=100 |

### Majority vote

|  | Pred conflict | Pred no_conflict/esc |
|---|---:|---:|
| **Truth conflict** | TP=100 | FN=0 |
| **Truth no_conflict** | FP=100 | TN=0 |

### Evidence-weighted committee

|  | Pred conflict | Pred no_conflict/esc |
|---|---:|---:|
| **Truth conflict** | TP=88 | FN=12 |
| **Truth no_conflict** | FP=100 | TN=0 |

## Per-family committee accuracy

| Family | N | Committee correct |
|---|---:|---:|
| aliasing_contract | 17 | 13/17 |
| aliasing_safe_copy | 14 | 0/14 |
| boundary_contract | 17 | 17/17 |
| boundary_dual_api | 15 | 0/15 |
| case_dual_api | 14 | 0/14 |
| case_sensitivity | 16 | 15/16 |
| cross_file_orthogonal | 14 | 0/14 |
| error_contract | 16 | 15/16 |
| error_dual_api | 14 | 0/14 |
| ordering_default | 17 | 14/17 |
| ordering_dual_api | 15 | 0/15 |
| sentinel_default | 17 | 14/17 |
| sentinel_dual_api | 14 | 0/14 |

