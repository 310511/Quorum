# Hard semantic benchmark pair

- Conflict type: `default_semantics`
- Ground truth: `conflict`
- Notes: Branch A changes DEFAULT_LIMIT 10->3; Branch B asserts old default length
- Validation: Branch A tests pass, Branch B tests pass, merged tests fail (semantic conflict).
