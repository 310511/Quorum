# Hard semantic benchmark pair

- Conflict type: `rename_stale_reference`
- Ground truth: `conflict`
- Notes: Branch A renames compute_parser_2_total->compute_parser_2_total_v2; Branch B adds caller of compute_parser_2_total
- Validation: Branch A tests pass, Branch B tests pass, merged tests fail (semantic conflict).
