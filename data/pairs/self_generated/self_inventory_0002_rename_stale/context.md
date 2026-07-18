# Self-generated semantic conflict

- Source fixture: `C:\Users\punya mittal\data\examples\generated\inventory_0002`
- Branch A renames `compute_available` to `compute_available_v2` and updates existing callers.
- Branch B independently adds a new caller of `compute_available` in a new file.
- Each branch passes tests independently and their file changes do not overlap.
- The merged tree fails because Branch B retains the removed symbol.
