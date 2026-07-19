# Hard semantic benchmark pair

- Conflict type: `import_drift`
- Ground truth: `conflict`
- Notes: Branch A moves normalize_billing_1_token; Branch B still imports billing_1_utils
- Validation: Branch A tests pass, Branch B tests pass, merged tests fail (semantic conflict).
