# Hard semantic conflict (records1)

- Family: `error_contract`
- Difficulty: `hard`
- Description: Exception suppression invalidates the new validation strategy.
- Hidden invariant: Non-numeric input is reported as invalid.
- Left intent: Make parsing tolerant by returning a numeric fallback.
- Right intent: Add validation that detects invalid input through parse failures.
- Record id: `e206115c-9e7c-4e23-8357-48f14bbb5858`
