# Hard semantic conflict (records1)

- Family: `sentinel_default`
- Difficulty: `hard`
- Description: The new consumer compiles but receives a different sentinel meaning.
- Hidden invariant: An omitted limit permits values below the configured default.
- Left intent: Use zero as the neutral value for an omitted limit.
- Right intent: Add admission logic that relies on the configured missing-value default.
- Record id: `7f9eabbe-391e-4cfb-a1e0-8a96e4b05808`
