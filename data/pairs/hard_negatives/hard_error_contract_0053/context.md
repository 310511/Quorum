# Hard semantic conflict (records1)

- Family: `error_contract`
- Difficulty: `hard`
- Description: Exception suppression invalidates the new validation strategy.
- Hidden invariant: Non-numeric input is reported as invalid.
- Left intent: Make parsing tolerant by returning a numeric fallback.
- Right intent: Add validation that detects invalid input through parse failures.
- Record id: `bcaa58de-2955-450a-9de7-9d94f3d60981`
