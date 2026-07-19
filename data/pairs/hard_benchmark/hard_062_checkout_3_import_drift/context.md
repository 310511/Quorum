# Hard semantic benchmark pair

- Conflict type: `import_drift`
- Ground truth: `conflict`
- Notes: Branch A moves normalize_checkout_3_token; Branch B still imports checkout_3_utils
- Validation: Branch A tests pass, Branch B tests pass, merged tests fail (semantic conflict).
