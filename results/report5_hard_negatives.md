# Five-system report — hard_negatives

- Raw: `run_20260718T224427Z.json`
- Structured: `run_hard_negatives_structured_final.json`
- N=100 · labels={'conflict': 100}
- Offline re-adjudication via `publication.predict_systems`

| System | Acc | Prec | Recall | Spec | F1 | BalAcc | MCC | Cov | Esc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Single-model baseline | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.00 | 100.0% | 0.0% |
| Majority vote | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% | 50.0% | 0.00 | 100.0% | 0.0% |
| Current escalation policy | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.00 | 0.0% | 100.0% |
| Evidence-weighted committee (raw) | 83.0% | 100.0% | 96.5% | 0.0% | 98.2% | 48.3% | 0.00 | 86.0% | 14.0% |
| Evidence-weighted + structured AST | 34.0% | 100.0% | 91.9% | 0.0% | 95.8% | 45.9% | 0.00 | 37.0% | 63.0% |

