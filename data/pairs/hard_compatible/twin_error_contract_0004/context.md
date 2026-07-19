# Hard compatible twin (verified true negative)

- Family: `error_contract`
- Description: Left adds a docstring only (parse still raises ValueError, no silent fallback); right's validator still catches it, so invalid input is still rejected after merge.
- Preserved invariant: Non-numeric input is still reported as invalid.
- Left intent: Document parsing helper (still raises ValueError on bad input).
- Right intent: Add validation that detects invalid input via parse failures.
- Validation: branch A tests pass, branch B tests + oracle pass, merged tests + semantic oracle PASS (merge is safe).
