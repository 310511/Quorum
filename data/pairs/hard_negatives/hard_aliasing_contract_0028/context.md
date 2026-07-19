# Hard semantic conflict (records1)

- Family: `aliasing_contract`
- Difficulty: `hard`
- Description: The optimization turns a local mutation into external state corruption.
- Hidden invariant: Read-style helpers never mutate caller-owned input.
- Left intent: Avoid an unnecessary list copy.
- Right intent: Add a convenience helper that edits its selected working set.
- Record id: `59bb5627-0985-4e8a-a3e7-334762dd7fca`
