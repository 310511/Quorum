# Hard semantic conflict (records1)

- Family: `sentinel_default`
- Difficulty: `hard`
- Description: The new consumer compiles but receives a different sentinel meaning.
- Hidden invariant: An omitted limit permits values below the configured default.
- Left intent: Use zero as the neutral value for an omitted limit.
- Right intent: Add admission logic that relies on the configured missing-value default.
- Record id: `315a5bf0-99ff-49a4-a312-63f84d626f5e`
