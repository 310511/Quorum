# Adjudicator v3 Verification Audit

Independent checks requested before treating the 99% blind result as publishable.
Adjudicator *logic* was not changed during this audit (freeze banner docstring only).

## 1. Ground-truth isolation

**PASS.** `adjudicate_v2` does not access labels or oracles.

- Function signature: `['results', 'branch_a_diff', 'branch_b_diff', 'structured_delta']`
- Forbidden source hits: `none`
- Unexpected parameters: `none`

adjudicate_v2 consumes ModelResult list + diffs (+ optional AST delta). ground_truth is read only AFTER prediction, for scoring in the offline evaluator — never passed into adjudicate_v2.

The offline evaluator reads `ground_truth` **only after** the prediction,
solely to compute metrics and the flip table.

## 2. Frozen model outputs (SHA-256)

Identical model outputs → different adjudication → improved metrics.

| Corpus | File | N | File SHA-256 | Model-outputs-only SHA-256 |
|---|---|---:|---|---|
| blind_eval | `results/run_blind_eval_raw_final.json` | 200 | `84e6499179d485b7023c40209ca552bb96de2cc128eab254d53c74b657f3ca78` | `77eb9eac58ec3c33c8c782e1a41893b37cc3149355652607eb5bd1bf1f715cca` |
| hard_negatives | `results/run_20260718T224427Z.json` | 100 | `f40859623492f4daac85e265dace055cba510954c0524a11c874dae922dda8d1` | `6c7d32d223a920df3419abe0eae3fc2b64c07cf9628454982096b3651ce33126` |
| hard_compatible_partial | `results/twins_raw_checkpoint.json` | 54 | `cb1cc62a3a11acd28f0a1e995589c3c1ac58289720e4c04472f9fc1fc7c7af71` | `a36f325117d13a11d1dcc2d2728d66f35b555d7b2a7248f2c322de773e5ad81a` |

## 3. Decision flips (old → new)

### blind_eval (N=200, flips=113)

Summary: `{'wrong_to_correct': 111, 'unchanged_correct': 87, 'wrong_to_wrong': 1, 'correct_to_wrong': 1}`

| Pair | Old | New | GT | Bucket | Reason |
|---|---|---|---|---|---|
| `03231ac0449792ff` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `032e64e7176c9bdb` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `0331da9ce58944e4` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `04438ea270d9411c` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `044a7311799aace2` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `04715166d244100f` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `052aec629d626acc` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `091abc8c6a81d161` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `09e047da636a13e3` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `10a788790300ae8e` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `113742ad0fe44d42` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `14b5debb01ede9aa` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `16cf22bb1287ec59` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `1842c001f679b2f3` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `1cfabcd981415ce7` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `1d31507323d178ae` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `1e3048475a39d2a7` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `1fdf06b0acf843c1` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `2079da0582a7dbc6` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `20da8986c49e8130` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `24d6cf316635cbba` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `25b55e9654079983` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `2739bd54d39c9c41` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `294c664a14de9b74` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `2acba6653222a60c` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `2b11e8510b66823e` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `3243a69d60213c51` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `397638d461e08caa` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `399daa1263969c10` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `3fb25addae660e9e` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `3fd5184c77392ede` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `41afddff8a756842` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `45324a2611b6910a` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `45f5fb1e9711cb09` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `4764e5af79659eec` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `4a6f18287ff10a14` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `4b1b609837d30e21` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `4c8765f1c0f1656e` | no_conflict | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `4cc42a8ab174cc18` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `531dc75e1d8ccb5f` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `53ff39b28eeb17f8` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `563f2f6fbc2d529a` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `58750c71e21f2f6d` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `59a15b8c9fd82d99` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `5e6ba466fac58bb4` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `5fa6271192f6f710` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `61759bff6d55cee2` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `66d85ac83242e80c` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `66e8e93ae3b81e50` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `67a53d687eab0e24` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `69ebdaa9ef346f66` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `6a1d9070709192f7` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `71c2d46d2a443fdc` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `7251e8e4f4e4672b` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `7633a838f7a2aeb4` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `766305a942189e0f` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `77b2ed91d53f7ecb` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `78dfdaddbef0bf3f` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `7d76d7a3d82e0062` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `7d7d49b90dec7a9f` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `7d7e4f185b5f4ed2` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `7f6215c8c2d72ae8` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `849cf408f8c88bb2` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `85a3a2334aaadc49` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `87b9e5fa4ea20ad0` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `887f73ccec9cc7ad` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `8a116e208c673428` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `8d42dcd019ae2cd8` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `924e8b26f78a9f5b` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `939a9e411b3426ea` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `98b8b1e4b584a88c` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `9aa87bae12174e4e` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `9eb578e52bfe06a0` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `9f317ad404d1247c` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `a2f0fcecacb1b988` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `a8b5a7f5078982b8` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `aa856882e3b900d7` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `aae23a1e0e3d29b7` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `ab213189ea513af0` | no_conflict | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `ab59c9e47dbab097` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `ac3195522586cc84` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `acb4fdf2184e6c48` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `b1d20992039e157f` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `b42e858a8c5b0c4d` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `bd19fd91ce2303e3` | no_conflict | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `c357e9cc33faefde` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `ca49b44be4901428` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `cdd9ef567322ea35` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `d334b49ab37720a4` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `d364ec7df2339361` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `d37cd89109f0a264` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `d38cd6dd5fa2248b` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `d4497ba843eb5924` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `d4adbb34da588211` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `d5f10684ecf71d4d` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `d7b024344dac0e50` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `d84e32abe003073c` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `db0fa6fa0db53982` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `dbf4cf9d4d35a2df` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `e2b7e12af33c9763` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `e4d70c9fae7079f0` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `e6095ca42e19cebb` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `e89d0b04627e4bdd` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `eb83946c68b62faa` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `f1338fc1b2193f76` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `f37cfa0dad1e3d55` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `f3c705c55285920e` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `f522f7d24223b273` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `f7220ff3432eae57` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `f8b0f91a171bc40b` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `fe69e6e85b2bdbcf` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `291104c4780e2f15` | conflict | no_conflict | conflict | correct_to_wrong | speculative / incomplete conflict rejected (no causal break) |
| `20efb98d0b1e45a0` | error | no_conflict | conflict | wrong_to_wrong | speculative / incomplete conflict rejected (no causal break) |

Of 113 flips: **111 wrong→correct**, **1 correct→wrong**.

### hard_negatives (N=100, flips=21)

Summary: `{'wrong_to_correct': 13, 'unchanged_correct': 79, 'correct_to_wrong': 4, 'wrong_to_wrong': 4}`

| Pair | Old | New | GT | Bucket | Reason |
|---|---|---|---|---|---|
| `hard_aliasing_contract_0004` | no_conflict | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `hard_boundary_contract_0001` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `hard_boundary_contract_0013` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `hard_case_sensitivity_0012` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `hard_case_sensitivity_0018` | no_conflict | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `hard_case_sensitivity_0072` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `hard_error_contract_0023` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `hard_error_contract_0029` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `hard_error_contract_0059` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `hard_error_contract_0071` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `hard_ordering_default_0068` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `hard_ordering_default_0080` | no_conflict | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `hard_sentinel_default_0021` | error | conflict | conflict | wrong_to_correct | causal chain detected on grounded cross-branch risk symbol |
| `hard_aliasing_contract_0046` | conflict | no_conflict | conflict | correct_to_wrong | speculative / incomplete conflict rejected (no causal break) |
| `hard_error_contract_0041` | conflict | no_conflict | conflict | correct_to_wrong | speculative / incomplete conflict rejected (no causal break) |
| `hard_error_contract_0047` | conflict | no_conflict | conflict | correct_to_wrong | speculative / incomplete conflict rejected (no causal break) |
| `hard_error_contract_0065` | conflict | no_conflict | conflict | correct_to_wrong | speculative / incomplete conflict rejected (no causal break) |
| `hard_error_contract_0005` | error | no_conflict | conflict | wrong_to_wrong | speculative / incomplete conflict rejected (no causal break) |
| `hard_error_contract_0053` | error | no_conflict | conflict | wrong_to_wrong | speculative / incomplete conflict rejected (no causal break) |
| `hard_error_contract_0077` | error | no_conflict | conflict | wrong_to_wrong | speculative / incomplete conflict rejected (no causal break) |
| `hard_error_contract_0095` | error | no_conflict | conflict | wrong_to_wrong | speculative / incomplete conflict rejected (no causal break) |

Of 21 flips: **13 wrong→correct**, **4 correct→wrong**.

### hard_compatible_partial (N=54, flips=35)

Summary: `{'wrong_to_correct': 35, 'unchanged_correct': 19}`

| Pair | Old | New | GT | Bucket | Reason |
|---|---|---|---|---|---|
| `twin_aliasing_contract_0001` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_aliasing_contract_0002` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_aliasing_contract_0003` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_aliasing_contract_0004` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_aliasing_contract_0005` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_aliasing_contract_0006` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_aliasing_contract_0007` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_aliasing_contract_0008` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_aliasing_contract_0009` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_aliasing_contract_0011` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_aliasing_contract_0012` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_aliasing_contract_0013` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_aliasing_contract_0014` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_aliasing_contract_0015` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_aliasing_contract_0016` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_aliasing_contract_0017` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_boundary_contract_0003` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_boundary_contract_0004` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_boundary_contract_0005` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_boundary_contract_0006` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_boundary_contract_0007` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_boundary_contract_0008` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_boundary_contract_0009` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_boundary_contract_0010` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_boundary_contract_0011` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_boundary_contract_0012` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_boundary_contract_0013` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_boundary_contract_0014` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_boundary_contract_0015` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_boundary_contract_0016` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_boundary_contract_0017` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_case_sensitivity_0013` | error | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_case_sensitivity_0017` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_error_contract_0002` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |
| `twin_error_contract_0003` | conflict | no_conflict | no_conflict | wrong_to_correct | missing cross-branch dependency (no behavior-changed symbol shared) |

Of 35 flips: **35 wrong→correct**, **0 correct→wrong**.

## Remaining misses (expected)

Blind FN=2 are exception-contract pairs where **no model** produced a
valid causal rationale. The gate correctly refused to invent conflict
evidence. Those belong to first-pass reasoning, not adjudication.

## Freeze declaration

**Adjudicator v3 is frozen.** Do not modify `quorum/adjudicate_v2.py`
until after: full re-eval with frozen policy, evaluation chapter draft,
and an independent leakage/implementation audit.

Artifacts:
- `results/adjudicator_v3_freeze.json`
- `results/adjudicator_v3_flips.json`
- `results/adjudicator_v3_offline.md` (metrics)

