# Hard compatible twin (verified true negative)

- Family: `sentinel_default`
- Description: Left adds a docstring only (default stays 137); right's admission check still resolves a missing limit to the original default.
- Preserved invariant: An omitted limit still resolves to the original non-zero default.
- Left intent: Document limit resolution (default value unchanged).
- Right intent: Add admission logic relying on the configured missing-value default.
- Validation: branch A tests pass, branch B tests + oracle pass, merged tests + semantic oracle PASS (merge is safe).
