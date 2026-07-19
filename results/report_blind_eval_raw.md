# Report — blind_eval_raw

- Run: `run_blind_eval_raw_final.json`
- N=200 · labels={'no_conflict': 100, 'conflict': 100}

| System | Acc | Prec | Recall | Spec | F1 | BalAcc | MCC | Cov | Esc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 50.0% | 0.0% | 0.0% | 100.0% | 0.0% | 50.0% | 0.00 | 100.0% | 0.0% |
| Majority | 50.0% | 50.0% | 100.0% | 0.0% | 66.7% | 50.0% | 0.00 | 100.0% | 0.0% |
| Committee | 44.0% | 46.8% | 88.0% | 0.0% | 61.1% | 44.0% | -0.25 | 95.5% | 4.5% |

