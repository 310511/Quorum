# Hard compatible twin (verified true negative)

- Family: `case_sensitivity`
- Description: Left adds a docstring only (same_code still uses strict '=='); right's authorization check stays case-sensitive after merge.
- Preserved invariant: Authorization codes remain case-sensitive.
- Left intent: Document identity comparison (still case-sensitive).
- Right intent: Reuse identifier comparison for an authorization check.
- Validation: branch A tests pass, branch B tests + oracle pass, merged tests + semantic oracle PASS (merge is safe).
