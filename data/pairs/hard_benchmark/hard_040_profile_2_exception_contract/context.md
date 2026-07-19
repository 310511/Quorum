# Hard semantic benchmark pair

- Conflict type: `exception_contract`
- Ground truth: `conflict`
- Notes: Branch A changes exception type; Branch B still catches the old type
- Validation: Branch A tests pass, Branch B tests pass, merged tests fail (semantic conflict).
