# Self-generated semantic conflict

- Source fixture: `C:\Users\punya mittal\data\examples\generated\scoring_0003`
- Branch A renames `compute_total` to `compute_total_v2` and updates existing callers.
- Branch B independently adds a new caller of `compute_total` in a new file.
- Each branch passes tests independently and their file changes do not overlap.
- The merged tree fails because Branch B retains the removed symbol.
