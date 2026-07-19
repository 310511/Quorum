# Behavior-Break Adjudicator — Offline Evaluation

Same saved model outputs; only adjudication/scoring changed.

| Corpus | N | Policy | Acc | Prec | Recall | Spec | F1 | BalAcc | MCC | Esc |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| blind_eval | 200 | old | 44.0% | 46.8% | 88.0% | 0.0% | 61.1% | 44.0% | -0.25 | 0.0% |
| blind_eval | 200 | new | 99.0% | 100.0% | 98.0% | 100.0% | 99.0% | 99.0% | 0.98 | 0.0% |

New confusion: `corpus['new']['TP']=98` `corpus['new']['FP']=0` `corpus['new']['TN']=100` `corpus['new']['FN']=2`

Rules: `{'conflict_evidence_gate': 102, 'grounded_behavior_break': 98}`

| hard_negatives | 100 | old | 83.0% | 100.0% | 83.0% | 0.0% | 90.7% | 41.5% | 0.00 | 0.0% |
| hard_negatives | 100 | new | 92.0% | 100.0% | 92.0% | 0.0% | 95.8% | 46.0% | 0.00 | 0.0% |

New confusion: `corpus['new']['TP']=92` `corpus['new']['FP']=0` `corpus['new']['TN']=0` `corpus['new']['FN']=8`

Rules: `{'grounded_behavior_break': 92, 'conflict_evidence_gate': 8}`

| hard_compatible_partial | 49 | old | 34.7% | 0.0% | 0.0% | 35.4% | 0.0% | 17.7% | -0.19 | 0.0% |
| hard_compatible_partial | 49 | new | 100.0% | 0.0% | 0.0% | 100.0% | 0.0% | 50.0% | 0.00 | 0.0% |

New confusion: `corpus['new']['TP']=0` `corpus['new']['FP']=0` `corpus['new']['TN']=49` `corpus['new']['FN']=0`

Rules: `{'conflict_evidence_gate': 49}`

