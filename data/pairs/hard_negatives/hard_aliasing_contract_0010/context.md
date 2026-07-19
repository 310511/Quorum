# Hard semantic conflict (records1)

- Family: `aliasing_contract`
- Difficulty: `hard`
- Description: The optimization turns a local mutation into external state corruption.
- Hidden invariant: Read-style helpers never mutate caller-owned input.
- Left intent: Avoid an unnecessary list copy.
- Right intent: Add a convenience helper that edits its selected working set.
- Record id: `376b7266-9573-4c23-91c5-5611b4f6a29a`
