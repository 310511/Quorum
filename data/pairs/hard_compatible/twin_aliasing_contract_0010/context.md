# Hard compatible twin (verified true negative)

- Family: `aliasing_contract`
- Description: Left adds a docstring only (select still returns list(values), a real copy); right's mutation of the returned list never touches caller input.
- Preserved invariant: Read-style helpers never mutate caller-owned input.
- Left intent: Document selection helper (still returns a copy).
- Right intent: Add a convenience helper that edits its selected working set.
- Validation: branch A tests pass, branch B tests + oracle pass, merged tests + semantic oracle PASS (merge is safe).
