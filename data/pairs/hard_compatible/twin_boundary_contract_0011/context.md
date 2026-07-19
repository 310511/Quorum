# Hard compatible twin (verified true negative)

- Family: `boundary_contract`
- Description: Left adds a docstring only (comparison operator unchanged); right's new routing still sees strict '>' semantics, so a score exactly at the cutoff stays 'standard' after merge.
- Preserved invariant: A score exactly at the cutoff remains 'standard'.
- Left intent: Document eligibility helper (no behavior change).
- Right intent: Add routing that relies on the established strict threshold.
- Validation: branch A tests pass, branch B tests + oracle pass, merged tests + semantic oracle PASS (merge is safe).
