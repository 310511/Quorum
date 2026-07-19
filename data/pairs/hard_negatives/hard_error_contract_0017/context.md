# Hard semantic conflict (records1)

- Family: `error_contract`
- Difficulty: `hard`
- Description: Exception suppression invalidates the new validation strategy.
- Hidden invariant: Non-numeric input is reported as invalid.
- Left intent: Make parsing tolerant by returning a numeric fallback.
- Right intent: Add validation that detects invalid input through parse failures.
- Record id: `7b1e4323-0df0-4917-bc2c-43cc4463abe9`
