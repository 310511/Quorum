# Hard semantic benchmark pair

- Conflict type: `import_drift`
- Ground truth: `conflict`
- Notes: Branch A moves normalize_scheduler_2_token; Branch B still imports scheduler_2_utils
- Validation: Branch A tests pass, Branch B tests pass, merged tests fail (semantic conflict).
