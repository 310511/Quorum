# Hard compatible twin (verified true negative)

- Family: `ordering_default`
- Description: Left adds a docstring only (default reverse=False unchanged); right's helper still sees ascending order, so 'first' stays the smallest item.
- Preserved invariant: first(items) still returns the smallest item.
- Left intent: Document sort helper (default order unchanged).
- Right intent: Add a helper that treats the default first item as the minimum.
- Validation: branch A tests pass, branch B tests + oracle pass, merged tests + semantic oracle PASS (merge is safe).
