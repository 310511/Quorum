# Committee Mistake Catalog (Priority 1)

Diagnostic only — no model/adjudicator changes.

## Headline

- **blind_eval**: 112/200 errors (acc=44.0%) · FP=100 FN=3 esc-miss=9 · labels={'no_conflict': 100, 'conflict': 100}
- **hard_negatives**: 17/100 errors (acc=83.0%) · FP=0 FN=3 esc-miss=14 · labels={'conflict': 100}
- **hard_compatible**: 31/42 errors (acc=26.2%) · FP=31 FN=0 esc-miss=0 · labels={'no_conflict': 42}

## Category totals (all corpora)

| Category | Count |
|---|---:|
| `conflict_bias` | 99 |
| `hallucination` | 32 |
| `exception_contract` | 9 |
| `mutation` | 9 |
| `ownership` | 6 |
| `aliasing` | 5 |

## Dominant finding: conflict bias

On the leakage-free blind benchmark, the evidence-weighted committee scored **TN=0 / FP=100** on all compatible pairs (every dual-API twin and orthogonal pair predicted conflict). Majority vote is identical (always conflict). Baseline is the opposite extreme (always no_conflict). The committee's single largest weakness is accepting vague 'semantic incompatibility' without requiring evidence of an actual behavior break.

## blind_eval — every error (112)

| Pair | Family | GT | Committee | Why wrong | Category | Root cause |
|---|---|---|---|---|---|---|
| `03231ac0449792ff` | aliasing_safe_copy | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `032e64e7176c9bdb` | error_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `0331da9ce58944e4` | case_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `04438ea270d9411c` | aliasing_safe_copy | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `044a7311799aace2` | sentinel_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `04715166d244100f` | error_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `052aec629d626acc` | aliasing_safe_copy | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `091abc8c6a81d161` | sentinel_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `09e047da636a13e3` | case_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `10a788790300ae8e` | ordering_dual_api | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `113742ad0fe44d42` | cross_file_orthogonal | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `14b5debb01ede9aa` | ordering_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `16cf22bb1287ec59` | ordering_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `1842c001f679b2f3` | sentinel_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `1cfabcd981415ce7` | ordering_dual_api | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `1d31507323d178ae` | case_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `1e3048475a39d2a7` | boundary_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `1fdf06b0acf843c1` | ordering_dual_api | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `2079da0582a7dbc6` | aliasing_safe_copy | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `20da8986c49e8130` | aliasing_contract | conflict | escalate | Escalated instead of deciding; Ignored copy-vs-alias / ownership mutation hazard | `aliasing` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=aliasing_contract |
| `20efb98d0b1e45a0` | error_contract | conflict | escalate | Escalated instead of deciding; Missed exception-contract change (silent fallback vs raise) | `exception_contract` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=error_contract |
| `24d6cf316635cbba` | error_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `25b55e9654079983` | aliasing_safe_copy | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `2739bd54d39c9c41` | boundary_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `294c664a14de9b74` | cross_file_orthogonal | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `2acba6653222a60c` | case_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `2b11e8510b66823e` | ordering_default | conflict | escalate | Escalated instead of deciding; Missed default-semantics / sentinel mutation | `mutation` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=ordering_default |
| `3243a69d60213c51` | sentinel_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `397638d461e08caa` | cross_file_orthogonal | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `399daa1263969c10` | cross_file_orthogonal | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `3fb25addae660e9e` | case_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `3fd5184c77392ede` | aliasing_safe_copy | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `41afddff8a756842` | aliasing_safe_copy | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `45324a2611b6910a` | cross_file_orthogonal | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `45f5fb1e9711cb09` | aliasing_contract | conflict | escalate | Escalated instead of deciding; Ignored copy-vs-alias / ownership mutation hazard | `aliasing` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=aliasing_contract |
| `4764e5af79659eec` | error_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `4a6f18287ff10a14` | sentinel_default | conflict | escalate | Escalated instead of deciding; Missed default-semantics / sentinel mutation | `mutation` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=sentinel_default |
| `4b1b609837d30e21` | case_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `4c8765f1c0f1656e` | aliasing_contract | conflict | no_conflict | Ignored copy-vs-alias / ownership mutation hazard | `aliasing` | votes conflict=2 compatible=1 rule=weighted_evidence_vote; family=aliasing_contract |
| `4cc42a8ab174cc18` | sentinel_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `531dc75e1d8ccb5f` | case_dual_api | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `53ff39b28eeb17f8` | case_dual_api | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `563f2f6fbc2d529a` | cross_file_orthogonal | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `58750c71e21f2f6d` | sentinel_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `59a15b8c9fd82d99` | case_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `5e6ba466fac58bb4` | ordering_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `5fa6271192f6f710` | cross_file_orthogonal | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `61759bff6d55cee2` | ordering_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `66d85ac83242e80c` | case_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `66e8e93ae3b81e50` | ordering_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `67a53d687eab0e24` | aliasing_safe_copy | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `69ebdaa9ef346f66` | boundary_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `6a1d9070709192f7` | boundary_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `71c2d46d2a443fdc` | aliasing_safe_copy | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `7251e8e4f4e4672b` | cross_file_orthogonal | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `7633a838f7a2aeb4` | case_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `766305a942189e0f` | error_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `77b2ed91d53f7ecb` | error_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `78dfdaddbef0bf3f` | error_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `7d76d7a3d82e0062` | error_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `7d7d49b90dec7a9f` | ordering_default | conflict | escalate | Escalated instead of deciding; Missed default-semantics / sentinel mutation | `mutation` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=ordering_default |
| `7d7e4f185b5f4ed2` | sentinel_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `7f6215c8c2d72ae8` | error_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `849cf408f8c88bb2` | sentinel_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `85a3a2334aaadc49` | sentinel_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `87b9e5fa4ea20ad0` | case_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `887f73ccec9cc7ad` | cross_file_orthogonal | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `8a116e208c673428` | boundary_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `8d42dcd019ae2cd8` | sentinel_dual_api | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `924e8b26f78a9f5b` | sentinel_dual_api | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `939a9e411b3426ea` | sentinel_default | conflict | escalate | Escalated instead of deciding; Missed default-semantics / sentinel mutation | `mutation` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=sentinel_default |
| `98b8b1e4b584a88c` | boundary_dual_api | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `9aa87bae12174e4e` | sentinel_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `9eb578e52bfe06a0` | aliasing_safe_copy | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `9f317ad404d1247c` | error_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `a2f0fcecacb1b988` | sentinel_dual_api | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `a8b5a7f5078982b8` | sentinel_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `aa856882e3b900d7` | boundary_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `aae23a1e0e3d29b7` | ordering_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `ab213189ea513af0` | sentinel_default | conflict | no_conflict | Missed default-semantics / sentinel mutation | `mutation` | votes conflict=2 compatible=1 rule=weighted_evidence_vote; family=sentinel_default |
| `ab59c9e47dbab097` | ordering_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `ac3195522586cc84` | error_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `acb4fdf2184e6c48` | cross_file_orthogonal | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `b1d20992039e157f` | error_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `b42e858a8c5b0c4d` | boundary_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `bd19fd91ce2303e3` | ordering_default | conflict | no_conflict | Missed default-semantics / sentinel mutation | `mutation` | votes conflict=2 compatible=1 rule=weighted_evidence_vote; family=ordering_default |
| `c357e9cc33faefde` | case_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `ca49b44be4901428` | aliasing_safe_copy | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `cdd9ef567322ea35` | boundary_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `d334b49ab37720a4` | case_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `d364ec7df2339361` | ordering_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `d37cd89109f0a264` | cross_file_orthogonal | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `d38cd6dd5fa2248b` | ordering_dual_api | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `d4497ba843eb5924` | boundary_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `d4adbb34da588211` | aliasing_safe_copy | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `d5f10684ecf71d4d` | ordering_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `d7b024344dac0e50` | error_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `d84e32abe003073c` | aliasing_safe_copy | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `db0fa6fa0db53982` | boundary_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `dbf4cf9d4d35a2df` | aliasing_safe_copy | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `e2b7e12af33c9763` | boundary_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `e4d70c9fae7079f0` | boundary_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `e6095ca42e19cebb` | boundary_dual_api | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `e89d0b04627e4bdd` | cross_file_orthogonal | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `eb83946c68b62faa` | cross_file_orthogonal | no_conflict | conflict | Hallucinated rename/stale dependency that is not in the diffs | `hallucination` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `f1338fc1b2193f76` | ordering_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `f37cfa0dad1e3d55` | boundary_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `f3c705c55285920e` | ordering_dual_api | no_conflict | conflict | Treated additive dual-API / docstring twin as incompatible APIs | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `f522f7d24223b273` | case_sensitivity | conflict | escalate | Escalated instead of deciding; Missed case-sensitivity contract | `ownership` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=case_sensitivity |
| `f7220ff3432eae57` | cross_file_orthogonal | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |
| `f8b0f91a171bc40b` | aliasing_contract | conflict | escalate | Escalated instead of deciding; Ignored copy-vs-alias / ownership mutation hazard | `aliasing` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=aliasing_contract |
| `fe69e6e85b2bdbcf` | error_dual_api | no_conflict | conflict | Predicted conflict without demonstrating a behavior break | `conflict_bias` | 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demon |

### Blind family × error category

| Family | `aliasing` | `conflict_bias` | `exception_contract` | `hallucination` | `mutation` | `ownership` | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| aliasing_contract | 4 | 0 | 0 | 0 | 0 | 0 | 4 |
| aliasing_safe_copy | 0 | 13 | 0 | 1 | 0 | 0 | 14 |
| boundary_dual_api | 0 | 13 | 0 | 2 | 0 | 0 | 15 |
| case_dual_api | 0 | 12 | 0 | 2 | 0 | 0 | 14 |
| case_sensitivity | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| cross_file_orthogonal | 0 | 7 | 0 | 7 | 0 | 0 | 14 |
| error_contract | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| error_dual_api | 0 | 14 | 0 | 0 | 0 | 0 | 14 |
| ordering_default | 0 | 0 | 0 | 0 | 3 | 0 | 3 |
| ordering_dual_api | 0 | 11 | 0 | 4 | 0 | 0 | 15 |
| sentinel_default | 0 | 0 | 0 | 0 | 3 | 0 | 3 |
| sentinel_dual_api | 0 | 11 | 0 | 3 | 0 | 0 | 14 |

## hard_negatives — every error (17)

| Pair | Family | GT | Committee | Why wrong | Category | Root cause |
|---|---|---|---|---|---|---|
| `hard_aliasing_contract_0004` | aliasing_contract | conflict | no_conflict | Ignored copy-vs-alias / ownership mutation hazard | `aliasing` | votes conflict=2 compatible=1 rule=weighted_evidence_vote; family=aliasing_contract |
| `hard_boundary_contract_0001` | boundary_contract | conflict | escalate | Escalated instead of deciding; Missed boundary/threshold contract change | `ownership` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=boundary_contract |
| `hard_boundary_contract_0013` | boundary_contract | conflict | escalate | Escalated instead of deciding; Missed boundary/threshold contract change | `ownership` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=boundary_contract |
| `hard_case_sensitivity_0012` | case_sensitivity | conflict | escalate | Escalated instead of deciding; Missed case-sensitivity contract | `ownership` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=case_sensitivity |
| `hard_case_sensitivity_0018` | case_sensitivity | conflict | no_conflict | Missed case-sensitivity contract | `ownership` | votes conflict=2 compatible=1 rule=weighted_evidence_vote; family=case_sensitivity |
| `hard_case_sensitivity_0072` | case_sensitivity | conflict | escalate | Escalated instead of deciding; Missed case-sensitivity contract | `ownership` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=case_sensitivity |
| `hard_error_contract_0005` | error_contract | conflict | escalate | Escalated instead of deciding; Missed exception-contract change (silent fallback vs raise) | `exception_contract` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=error_contract |
| `hard_error_contract_0023` | error_contract | conflict | escalate | Escalated instead of deciding; Missed exception-contract change (silent fallback vs raise) | `exception_contract` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=error_contract |
| `hard_error_contract_0029` | error_contract | conflict | escalate | Escalated instead of deciding; Missed exception-contract change (silent fallback vs raise) | `exception_contract` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=error_contract |
| `hard_error_contract_0053` | error_contract | conflict | escalate | Escalated instead of deciding; Missed exception-contract change (silent fallback vs raise) | `exception_contract` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=error_contract |
| `hard_error_contract_0059` | error_contract | conflict | escalate | Escalated instead of deciding; Missed exception-contract change (silent fallback vs raise) | `exception_contract` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=error_contract |
| `hard_error_contract_0071` | error_contract | conflict | escalate | Escalated instead of deciding; Missed exception-contract change (silent fallback vs raise) | `exception_contract` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=error_contract |
| `hard_error_contract_0077` | error_contract | conflict | escalate | Escalated instead of deciding; Missed exception-contract change (silent fallback vs raise) | `exception_contract` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=error_contract |
| `hard_error_contract_0095` | error_contract | conflict | escalate | Escalated instead of deciding; Missed exception-contract change (silent fallback vs raise) | `exception_contract` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=error_contract |
| `hard_ordering_default_0068` | ordering_default | conflict | escalate | Escalated instead of deciding; Missed default-semantics / sentinel mutation | `mutation` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=ordering_default |
| `hard_ordering_default_0080` | ordering_default | conflict | no_conflict | Missed default-semantics / sentinel mutation | `mutation` | votes conflict=2 compatible=1 rule=weighted_evidence_vote; family=ordering_default |
| `hard_sentinel_default_0021` | sentinel_default | conflict | escalate | Escalated instead of deciding; Missed default-semantics / sentinel mutation | `mutation` | votes conflict=2 compatible=1 rule=ambiguous_evidence; family=sentinel_default |

## hard_compatible — every error (31)

| Pair | Family | GT | Committee | Why wrong | Category | Root cause |
|---|---|---|---|---|---|---|
| `twin_aliasing_contract_0001` | aliasing_contract | no_conflict | conflict | Hallucinated semantic break on docstring-only left branch | `hallucination` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_aliasing_contract_0002` | aliasing_contract | no_conflict | conflict | Hallucinated semantic break on docstring-only left branch | `hallucination` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_aliasing_contract_0003` | aliasing_contract | no_conflict | conflict | Hallucinated semantic break on docstring-only left branch | `hallucination` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_aliasing_contract_0004` | aliasing_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_aliasing_contract_0005` | aliasing_contract | no_conflict | conflict | Hallucinated semantic break on docstring-only left branch | `hallucination` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_aliasing_contract_0006` | aliasing_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_aliasing_contract_0007` | aliasing_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_aliasing_contract_0008` | aliasing_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_aliasing_contract_0009` | aliasing_contract | no_conflict | conflict | Hallucinated semantic break on docstring-only left branch | `hallucination` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_aliasing_contract_0011` | aliasing_contract | no_conflict | conflict | Hallucinated semantic break on docstring-only left branch | `hallucination` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_aliasing_contract_0012` | aliasing_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_aliasing_contract_0013` | aliasing_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_aliasing_contract_0014` | aliasing_contract | no_conflict | conflict | Hallucinated semantic break on docstring-only left branch | `hallucination` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_aliasing_contract_0015` | aliasing_contract | no_conflict | conflict | Hallucinated semantic break on docstring-only left branch | `hallucination` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_aliasing_contract_0016` | aliasing_contract | no_conflict | conflict | Hallucinated semantic break on docstring-only left branch | `hallucination` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_aliasing_contract_0017` | aliasing_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_boundary_contract_0003` | boundary_contract | no_conflict | conflict | Hallucinated semantic break on docstring-only left branch | `hallucination` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_boundary_contract_0004` | boundary_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_boundary_contract_0005` | boundary_contract | no_conflict | conflict | Hallucinated semantic break on docstring-only left branch | `hallucination` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_boundary_contract_0006` | boundary_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_boundary_contract_0007` | boundary_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_boundary_contract_0008` | boundary_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_boundary_contract_0009` | boundary_contract | no_conflict | conflict | Hallucinated semantic break on docstring-only left branch | `hallucination` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_boundary_contract_0010` | boundary_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_boundary_contract_0011` | boundary_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_boundary_contract_0012` | boundary_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_boundary_contract_0013` | boundary_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_boundary_contract_0014` | boundary_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_boundary_contract_0015` | boundary_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_boundary_contract_0016` | boundary_contract | no_conflict | conflict | Conflict-biased vote on behavior-preserving twin | `conflict_bias` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |
| `twin_boundary_contract_0017` | boundary_contract | no_conflict | conflict | Hallucinated semantic break on docstring-only left branch | `hallucination` | 2/3 conflict votes; left branch is docstring-only; original semantics preserved |

## Deep dives (representative mistakes)

### `032e64e7176c9bdb` (blind_eval)

- GT: **no_conflict** · Committee: **conflict** · Baseline: no_conflict
- Family: `error_dual_api`
- Category: `conflict_bias` — Predicted conflict without demonstrating a behavior break
- Root cause: 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demonstrated
- Adjudication: `rationale_dominance` — gemma3:4b gave the strongest grounded rationale (score 0.76 vs 0.51, margin 0.25 >= 0.12); verdict 'conflict' accepted over deepseek-coder:6.7b despite the vote split. Grounded evidence: ['bool', 'except', 'int', 'parse_count_054', 'parse_c
- Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branch A introduces two new functions: `parse_count_054` and `parse_count_soft_054`. Branch B introduces a function `valid_count_054` that uses `parse_count_054` and checks for a ValueError. This crea
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in Branch B do not introduce any semantic conflicts with the existing codebase or logic of Branch A. The new function `valid_count_054` is logically consistent with the existing `parse_cou
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would contain both the original `parse_count_054` function and the new `valid_count_054` function with its dependency on `parse_count_054`. This inconsistency could lead to unexpected 

### `113742ad0fe44d42` (blind_eval)

- GT: **no_conflict** · Committee: **conflict** · Baseline: no_conflict
- Family: `cross_file_orthogonal`
- Category: `conflict_bias` — Predicted conflict without demonstrating a behavior break
- Root cause: 2/3 models voted conflict; adjudicator rule=rationale_dominance; no API break / invariant violation / stale caller demonstrated
- Adjudication: `rationale_dominance` — gemma3:4b gave the strongest grounded rationale (score 0.87 vs 0.58, margin 0.29 >= 0.12); verdict 'conflict' accepted over deepseek-coder:6.7b despite the vote split. Grounded evidence: ['amount', 'assertequal', 'boosted_score_021', 'clamp
- Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branch A introduces `boosted_score_021` which uses the `clamp_021` function with a boost parameter. Branch B introduces `discounted_fee_021` which uses `clamp_021` with a discount parameter. The test 
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are logically correct without any semantic conflict. The functions `score_021` and `fee_021` from Branch A and `boosted_score_021` and `discounted_fee_021` from Branch B d
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use `boosted_score_021` from Branch A in a context where `discounted_fee_021` from Branch B is expected, indicating a semantic conflict.

### `4c8765f1c0f1656e` (blind_eval)

- GT: **conflict** · Committee: **no_conflict** · Baseline: no_conflict
- Family: `aliasing_contract`
- Category: `aliasing` — Ignored copy-vs-alias / ownership mutation hazard
- Root cause: votes conflict=2 compatible=1 rule=weighted_evidence_vote; family=aliasing_contract
- Adjudication: `weighted_evidence_vote` — Rationale quality is comparable (margin 0.10 < 0.12); confidence-weighted evidence favors 'no_conflict' (conflict=0.62 vs no_conflict=0.68, gap 0.06).
- Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branch A introduces a simplified version of `select_052` that directly returns the input list. Branch B adds a new function `without_last_052` which uses `select_052` and then removes the last element
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are logically compatible since the function `select_052` is used by the new test case `test_result_drops_last` in branch B and it does not conflict with the existing imple
  - `llama3.2:3b` → `conflict` (conf=0.8): Branch A renames `select_052` to return the original list, while Branch B introduces a new function `without_last_052` that calls the renamed `select_052`. This semantic change breaks logical consiste

### `twin_aliasing_contract_0001` (hard_compatible)

- GT: **no_conflict** · Committee: **conflict** · Baseline: no_conflict
- Family: `aliasing_contract`
- Category: `hallucination` — Hallucinated semantic break on docstring-only left branch
- Root cause: 2/3 conflict votes; left branch is docstring-only; original semantics preserved
- Adjudication: `rationale_dominance` — llama3.2:3b gave the strongest grounded rationale (score 0.65 vs 0.00, margin 0.65 >= 0.12); verdict 'conflict' accepted over deepseek-coder:6.7b despite the vote split. Grounded evidence: ['copy', 'select_1', 'values', 'without_last_1'].
- Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branch A introduces a docstring to `select_1` which is safe. Branch B modifies the result of `select_1` by removing the last element from the list. This creates an unexpected side effect and violates 
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in Branch B do not introduce any new semantic conflicts or break the existing codebase as per the preserved invariant of 'Read-style helpers never mutate caller-owned input'.
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would have both the original `select_1` function that returns a copy of values and the new `without_last_1` function that modifies the returned list, which could lead to unexpected beh

## Implications for Priority 2–3 (do not implement yet)

1. **Conflict bias** dominates: every blind compatible pair was labeled conflict. Adjudication must require evidence of an *actual behavior break* (API break, violated invariant, stale caller, ownership violation, contract mismatch), not mere 'semantic difference' or 'duplicate helpers'.
2. **Evidence scoring** currently rewards identifier overlap and confident conflict narratives; it does not penalize speculative / hallucinated breaks on docstring-only or dual-API twins.
3. False negatives on hard conflicts are fewer and concentrated in aliasing / ordering / sentinel / error families where the invariant is subtle.

## Artifacts

- `results/error_catalog.json` — full machine-readable catalog
- `results/error_analysis.md` — this report

