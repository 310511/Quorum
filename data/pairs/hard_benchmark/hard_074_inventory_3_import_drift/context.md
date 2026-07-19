# Hard semantic benchmark pair

- Conflict type: `import_drift`
- Ground truth: `conflict`
- Notes: Branch A moves normalize_inventory_3_token; Branch B still imports inventory_3_utils
- Validation: Branch A tests pass, Branch B tests pass, merged tests fail (semantic conflict).
