# Five-system report — cooperbench_python

- Raw: `run_20260718T182612Z_cooper_raw.json`
- Structured: `run_20260718T182612Z_cooper_structured.json`
- N=16 · labels={'conflict': 9, 'no_conflict': 7}
- Offline re-adjudication via `publication.predict_systems`

| System | Acc | Prec | Recall | Spec | F1 | BalAcc | MCC | Cov | Esc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Single-model baseline | 56.2% | 60.0% | 66.7% | 42.9% | 63.2% | 54.8% | 0.10 | 100.0% | 0.0% |
| Majority vote | 56.2% | 56.2% | 100.0% | 0.0% | 72.0% | 50.0% | 0.00 | 100.0% | 0.0% |
| Current escalation policy | 6.2% | 100.0% | 100.0% | 0.0% | 100.0% | 50.0% | 0.00 | 6.2% | 93.8% |
| Evidence-weighted committee (raw) | 56.2% | 66.7% | 88.9% | 20.0% | 76.2% | 54.4% | 0.12 | 87.5% | 12.5% |
| Evidence-weighted + structured AST | 56.2% | 60.0% | 100.0% | 0.0% | 75.0% | 50.0% | 0.00 | 93.8% | 6.2% |

