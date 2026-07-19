# Hard semantic conflict (records1)

- Family: `error_contract`
- Difficulty: `hard`
- Description: Exception suppression invalidates the new validation strategy.
- Hidden invariant: Non-numeric input is reported as invalid.
- Left intent: Make parsing tolerant by returning a numeric fallback.
- Right intent: Add validation that detects invalid input through parse failures.
- Record id: `8745770d-6ede-4071-a8ca-2319dea938af`
