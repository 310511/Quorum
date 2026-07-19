# Hard semantic benchmark pair

- Conflict type: `return_contract`
- Ground truth: `conflict`
- Notes: Branch A nests score under meta; Branch B still reads top-level score
- Validation: Branch A tests pass, Branch B tests pass, merged tests fail (semantic conflict).
