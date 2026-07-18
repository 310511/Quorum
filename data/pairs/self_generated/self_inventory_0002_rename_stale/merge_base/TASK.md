# Task for fixture inventory_0002

Add a function `adjust_available(stock: int, reserved: int) -> int` that returns `clamp_0002(stock - reserved)`.

Preserve `compute_available` and `aggregate_available`.
Add unit tests covering a positive and a negative result.
Example expectation for inputs (20, 5): 15.
