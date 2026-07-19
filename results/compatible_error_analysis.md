# Compatible Example Error Analysis

Corpus: `hard_benchmark` raw run `run_20260718T225424Z.json`
Compatible examples: **30**

- Committee correct (TN): 2
- Committee false conflict (FP): 27
- Committee escalate: 1

## `hard_10000_profile_ok0_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branches A and B introduce completely different functions (`alpha_profile_ok0` and `beta_profile_ok0`) with distinct logic and signatures. Merging these will result in a broken cod
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add new functionalities to the codebase without affecting existing functionality. Therefore, merging them should be se
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use `alpha_profile_ok0` from Branch A and `beta_profile_ok0` from Branch B, which are different functions with incompatible behavior.

## `hard_10001_metrics_ok1_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): While there's no textual merge conflict, the branches introduce fundamentally different functions (`alpha_metrics_ok1` and `beta_metrics_ok1`) with distinct behaviors. Merging thes
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add functions to the codebase without affecting existing functionality. The tests pass for all three versions of the c
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use functions from different modules (`alpha_metrics_ok1` and `beta_metrics_ok1`) which are not related to each other semantically, leading to a logical incon

## `hard_10002_checkout_ok2_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branches A and B introduce completely different functions (`alpha_checkout_ok2` and `beta_checkout_ok2`) with distinct logic (addition vs. multiplication) and separate test suites.
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add new functionalities to the codebase without affecting existing functionality. Therefore, merging them should be co
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged codebase would have two functions (`alpha_checkout_ok2` and `beta_checkout_ok2`) that perform different operations on the input value, but are called by tests with the s

## `hard_10003_cache_ok3_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branches A and B introduce completely different functions (`alpha_cache_ok3` and `beta_cache_ok3`) with distinct logic (addition vs. multiplication) and separate test suites. Mergi
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add new functionalities to the codebase without affecting existing functionality. The tests pass for all three version
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use functions from different branches (alpha_cache_ok3 and beta_cache_ok3) without a clear indication of which one to call in case of conflicts or when both a

## `hard_10004_ledger_ok4_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branches A and B implement different functions with the same name (`alpha_ledger_ok4` and `beta_ledger_ok4`) but perform entirely different calculations. Merging these branches wil
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add new functionalities to the codebase without affecting existing functionality. The tests pass for all three version
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged codebase would use the `alpha_ledger_ok4` function from Branch A, but it is not compatible with the expected behavior of using `beta_ledger_ok4` from Branch B.

## `hard_10005_analytics_ok5_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Both branches introduce separate analytics functions (`alpha_analytics_ok5` and `beta_analytics_ok5`) with different logic (addition vs. multiplication) and distinct test suites. M
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add new functionalities without affecting the existing ones. Therefore, merging them should be compatible.
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged function `alpha_analytics_ok5` will be called with the old name 'value' instead of the new name 'beta_value', which is used in Branch B's code.

## `hard_10006_warehouse_ok6_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branches A and B introduce completely different functions (`alpha_warehouse_ok6` and `beta_warehouse_ok6`) with distinct logic and signatures. Merging them would result in a broken
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add new functionalities to the codebase without affecting existing functionality. Therefore, merging them should be co
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged codebase would have two different functions (`alpha_warehouse_ok6` and `beta_warehouse_ok6`) that are called by the same test cases, which is logically inconsistent.

## `hard_10007_search_ok7_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branches A and B introduce completely different search functions (`alpha_search_ok7` and `beta_search_ok7`) with distinct logic (addition vs. multiplication) and separate test suit
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add new functionalities to the codebase without affecting existing functionality. Therefore, merging them should be se
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use `alpha_search_ok7` from Branch A, but it's not clear if the new module is intended to be used with the existing tests or if the tests should be updated to

## `hard_10008_parser_ok8_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `no_conflict`
- **Why committee conflict:** 1/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `no_conflict` (conf=0.95): The branches implement distinct functions (`alpha_parser_ok8` and `beta_parser_ok8`) with different logic (addition vs. multiplication) and separate test suites. There is no overla
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add new functionalities to the codebase without affecting existing functionality or changing APIs. The tests pass for 
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use `alpha_parser_ok8` for both testing and parsing, which is inconsistent because the original purpose of each function differs.

## `hard_10009_pricing_ok9_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branch A introduces a function `alpha_pricing_ok9` that adds 1 to its input, while Branch B introduces `beta_pricing_ok9` which multiplies its input by 2. Merging these branches wo
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add functions to the codebase without affecting existing functionality. The tests pass for all three versions of the c
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use `alpha_pricing_ok9` for both pricing calculations, which is not the intended behavior. The original codebase likely expects different pricing functions fo

## `hard_10010_payments_ok10_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branch A introduces a function `alpha_payments_ok10` that adds 1 to its input, while Branch B introduces a function `beta_payments_ok10` that multiplies its input by 2. Merging the
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add new functionalities to the codebase without affecting existing functionality. The tests pass for each branch and t
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged functions `alpha_payments_ok10` and `beta_payments_ok10` are logically incompatible because they perform different operations on the input value.

## `hard_10011_catalog_ok11_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branch A introduces a function `alpha_catalog_ok11` that adds one to its input, while Branch B introduces a function `beta_catalog_ok11` that multiplies its input by two. Merging t
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add functions to the codebase without affecting existing functionality or changing function names. The tests pass for 
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use functions from different branches (alpha_catalog_ok11 and beta_catalog_ok11) without a clear common interface or compatibility mechanism.

## `hard_10012_shipping_ok12_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branches A and B introduce completely different functions (`alpha_shipping_ok12` and `beta_shipping_ok12`) with distinct logic (addition vs. multiplication) and names. Merging thes
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): Based on the provided diffs, Branch A and Branch B are independent new modules that add entirely new functionalities to the codebase without any overlap in functionality or API cha
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use functions from different modules (`alpha_shipping_ok12` and `beta_shipping_ok12`) without a clear way to resolve the difference in behavior (adding vs mul

## `hard_10013_routing_ok13_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branch A introduces a function `alpha_routing_ok13` that adds 1 to its input, while Branch B introduces a function `beta_routing_ok13` that multiplies its input by 2. Merging these
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add new functionalities to the codebase without affecting existing functionality. The tests pass for both branches and
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use functions from different modules (`alpha_routing_ok13` and `beta_routing_ok13`) without a clear connection between them, leading to logical inconsistency.

## `hard_10014_inventory_ok14_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branch A introduces a function `alpha_inventory_ok14` that adds one to its input, while Branch B introduces a function `beta_inventory_ok14` that multiplies its input by two. Mergi
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add functions to the codebase without changing existing functionality or naming of functions. The tests pass for all t
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use functions from different branches (alpha_inventory_ok14 and beta_inventory_ok14) without a clear indication of which one to call in case of conflicts or i

## `hard_10015_tickets_ok15_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 1/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `no_conflict` (conf=0.95): The branches implement completely separate functions (`alpha_tickets_ok15` and `beta_tickets_ok15`) with different logic and test cases. There is no overlap in functionality or API
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add new functionalities to the codebase without affecting existing functionality. The tests pass for all three version
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use `beta_tickets_ok15` instead of `alpha_tickets_ok15`, which is not logically correct because the tests are written for `alpha_tickets_ok15`. This change br

## `hard_10016_scheduler_ok16_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branch A introduces a function `alpha_scheduler_ok16` that adds one to its input, while Branch B introduces a function `beta_scheduler_ok16` that multiplies its input by two. Mergi
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): Based on the provided diffs, Branch A (alpha_scheduler_ok16) adds a new function that increases an input value by one and Branch B (beta_scheduler_ok16) adds another function that 
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use both `alpha_scheduler_ok16` and `beta_scheduler_ok16`, which are functions from different branches with different implementations. This could lead to logi

## `hard_10017_notifier_ok17_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branches A and B introduce completely different functions (`alpha_notifier_ok17` and `beta_notifier_ok17`) with distinct logic (addition vs. multiplication) and separate test suite
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add new functionalities to the codebase without affecting existing functionality. Therefore, merging them should be se
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged notifier functions (`alpha_notifier_ok17` and `beta_notifier_ok17`) have different return types (int+1 vs int*2), which could lead to unexpected behavior if used interch

## `hard_10018_billing_ok18_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branch A introduces a function `alpha_billing_ok18` that adds 1 to its input, while Branch B introduces a function `beta_billing_ok18` that multiplies its input by 2. Merging these
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): Based on the provided diffs, Branch A (alpha) and Branch B (beta) are independent new modules that add entirely new functionalities to the codebase without any overlap in functiona
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use `alpha_billing_ok18` from Branch A, but it's not clear if this function is intended to be used with the same input values as in Branch B's `beta_billing_o

## `hard_10019_auth_ok19_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branch A introduces a function `alpha_auth_ok19` that adds 1 to its input, while Branch B introduces a function `beta_auth_ok19` that multiplies its input by 2. Merging these branc
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add new functionalities to the codebase without affecting existing functionality or changing APIs. The tests pass for 
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged codebase would use the `alpha_auth_ok19` function from Branch A, but it is not compatible with the expected behavior of the `beta_auth_ok19` function from Branch B.

## `hard_10020_profile_ok20_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branches A and B introduce completely different functions (`alpha_profile_ok20` and `beta_profile_ok20`) with distinct logic (addition vs. multiplication) and separate test suites.
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add entirely new functionalities to the codebase without altering existing functionality or introducing any potential 
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use `alpha_profile_ok20` from Branch A and `beta_profile_ok20` from Branch B, which are two different functions with incompatible behavior (adding vs multiply

## `hard_10021_metrics_ok21_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branches A and B introduce completely different functions (`alpha_metrics_ok21` and `beta_metrics_ok21`) with distinct logic and APIs. Merging them would result in a broken system 
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add entirely new functionalities to the codebase without affecting existing functionality. Therefore, merging these tw
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use functions from different modules (alpha_metrics_ok21 and beta_metrics_ok21) without a clear common interface or base class, leading to potential logical i

## `hard_10022_checkout_ok22_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branch A adds a function `alpha_checkout_ok22` that increments its input by one, while Branch B adds a function `beta_checkout_ok22` that multiplies its input by two. Merging these
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add functions to the codebase without affecting existing functionality. The tests pass for each branch separately but 
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged codebase would contain two functions (`alpha_checkout_ok22` and `beta_checkout_ok22`) that perform different operations on the input value, but both are called in the sa

## `hard_10023_cache_ok23_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `escalate`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branch A introduces a function `alpha_cache_ok23` that adds 1 to its input, while Branch B introduces a function `beta_cache_ok23` that multiplies its input by 2. Merging these bra
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add new functionalities to the codebase without affecting existing functionality or changing APIs. The tests pass for 
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged functions `alpha_cache_ok23` and `beta_cache_ok23` have different return values for the same input, which could lead to unexpected behavior if used together.

## `hard_10024_ledger_ok24_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branches A and B introduce completely different functions (`alpha_ledger_ok24` and `beta_ledger_ok24`) with distinct logic (addition vs. multiplication) and separate test suites. M
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add functions to the codebase without affecting existing functionality. The tests pass for all three versions of the c
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use functions from different branches (alpha_ledger_ok24 and beta_ledger_ok24) without a clear connection between them, which could lead to logical inconsiste

## `hard_10025_analytics_ok25_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branches A and B introduce completely different analytics functions with distinct logic (addition vs. multiplication) and separate test suites. Merging these branches will result i
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add new functionalities without affecting existing ones. The tests pass for all three versions of the codebase.
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged functions `alpha_analytics_ok25` and `beta_analytics_ok25` have different return values for the same input value, which could lead to unexpected behavior in the combined

## `hard_10026_warehouse_ok26_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `no_conflict`
- **Why committee conflict:** 1/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `no_conflict` (conf=0.95): The branches implement completely separate functions (`alpha_warehouse_ok26` and `beta_warehouse_ok26`) with different logic and test cases. There is no overlap in functionality or
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add new functionalities to the codebase without affecting existing functionality. The tests pass for all three version
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use functions from different modules (alpha_warehouse_ok26 and beta_warehouse_ok26) without a clear connection between them, leading to logical inconsistency.

## `hard_10027_search_ok27_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branch A adds a function `alpha_search_ok27` that increments its input by one, while Branch B adds a function `beta_search_ok27` that multiplies its input by two. Merging these bra
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): Based on the provided diffs, it appears that Branch A (alpha) and Branch B (beta) are independent new modules with no overlap in functionality or dependencies. Therefore, merging t
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged function `alpha_search_ok27` calls itself without any checks or modifications to handle the case where the input value is not an integer, which could lead to unexpected 

## `hard_10028_parser_ok28_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branch A adds a function `alpha_parser_ok28` that increments its input by one, while Branch B adds a function `beta_parser_ok28` that multiplies its input by two. Merging these bra
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): Based on the diffs provided, Branch A (alpha_parser_ok28) adds a new function that appears to be logically correct and Branch B (beta_parser_ok28) also adds a new function which is
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use `alpha_parser_ok28` from Branch A, but it's not clear if the new function is intended to be used with values that are also expected by `beta_parser_ok28` 

## `hard_10029_pricing_ok29_compatible`

- **Why compatible:** Generator builds two orthogonal new modules (alpha_*/beta_*) with independent tests; merge_base only has an identity helper; no shared symbols between branch overlays.
- **Baseline:** `no_conflict`
- **Committee:** `conflict`
- **Why committee conflict:** 2/3 models predicted conflict. Common failure mode: treating distinct new functions as incompatible APIs rather than additive modules.
- **Committee rationale reasonable?** False
- **Reconsider ground truth?** False
- **Notes:** Ground truth should NOT be reconsidered: branches add disjoint files. Committee FP is a model reasoning error, not label noise. However, context.md already disclosed 'Ground truth: no_conflict' and 'merged tests pass', so models that still predicted conflict actively ignored privileged validation text.

Model votes:
  - `gemma3:4b` → `conflict` (conf=0.95): Branches A and B introduce completely different pricing logic – one adds 1 to the input value, while the other multiplies it by 2. Merging these will result in a broken calculation
  - `deepseek-coder:6.7b` → `no_conflict` (conf=1.0): The changes in both branches are independent new modules that add functions to the codebase without affecting existing functionality or changing function signatures. The tests pass
  - `llama3.2:3b` → `conflict` (conf=0.8): The merged code would use `alpha_pricing_ok29` for both alpha and beta pricing, which is logically inconsistent since they operate on different values.

