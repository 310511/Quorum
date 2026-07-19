# Hard semantic conflict (records1)

- Family: `aliasing_contract`
- Difficulty: `hard`
- Description: The optimization turns a local mutation into external state corruption.
- Hidden invariant: Read-style helpers never mutate caller-owned input.
- Left intent: Avoid an unnecessary list copy.
- Right intent: Add a convenience helper that edits its selected working set.
- Record id: `f03d6ecc-5dc8-422d-b54a-93a8f0f3b1c5`
