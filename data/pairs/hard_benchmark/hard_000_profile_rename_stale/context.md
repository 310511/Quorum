# Hard semantic benchmark pair

- Conflict type: `rename_stale_reference`
- Ground truth: `conflict`
- Notes: Branch A renames compute_profile_total->compute_profile_total_v2; Branch B adds caller of compute_profile_total
- Validation: Branch A tests pass, Branch B tests pass, merged tests fail (semantic conflict).
