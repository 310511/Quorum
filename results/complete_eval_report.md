# Complete Five-System Evaluation Report

Generated: 2026-07-19T11:50:20Z

Offline scoring of saved live runs. Live blind_eval / hard_compatible
evals continue in the background and will be appended when finished.

## cooperbench_python (N=16)

Labels: `{'conflict': 9, 'no_conflict': 7}`

| System | Acc | Prec | Recall | Spec | F1 | BalAcc | MCC | Esc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Single-model baseline | 56.2% | 60.0% | 66.7% | 42.9% | 63.2% | 54.8% | 0.10 | 0.0% |
| Majority vote | 56.2% | 56.2% | 100.0% | 0.0% | 72.0% | 50.0% | 0.00 | 0.0% |
| Current escalation policy | 6.2% | 100.0% | 100.0% | 0.0% | 100.0% | 50.0% | 0.00 | 93.8% |
| Evidence-weighted committee (raw) | 56.2% | 66.7% | 88.9% | 20.0% | 76.2% | 54.4% | 0.12 | 12.5% |
| Evidence-weighted + structured AST | 56.2% | 60.0% | 100.0% | 0.0% | 75.0% | 50.0% | 0.00 | 6.2% |

## hard_negatives (N=100)

Labels: `{'conflict': 100}`

| System | Acc | Prec | Recall | Spec | F1 | BalAcc | MCC | Esc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Single-model baseline | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.00 | 0.0% |
| Majority vote | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% | 50.0% | 0.00 | 0.0% |
| Current escalation policy | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.00 | 100.0% |
| Evidence-weighted committee (raw) | 83.0% | 100.0% | 96.5% | 0.0% | 98.2% | 48.3% | 0.00 | 14.0% |
| Evidence-weighted + structured AST | 34.0% | 100.0% | 91.9% | 0.0% | 95.8% | 45.9% | 0.00 | 63.0% |

