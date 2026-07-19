# Hard semantic benchmark pair

- Conflict type: `signature_break`
- Ground truth: `conflict`
- Notes: Branch A makes quantity/priority keyword-only; Branch B still calls positionally
- Validation: Branch A tests pass, Branch B tests pass, merged tests fail (semantic conflict).
