# Self-generated semantic conflict

- Source fixture: `C:\Users\punya mittal\data\examples\generated\shipping_0004`
- Branch A renames `compute_cost` to `compute_cost_v2` and updates existing callers.
- Branch B independently adds a new caller of `compute_cost` in a new file.
- Each branch passes tests independently and their file changes do not overlap.
- The merged tree fails because Branch B retains the removed symbol.
