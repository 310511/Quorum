# Self-generated semantic conflict

- Source fixture: `C:\Users\punya mittal\data\examples\example_1`
- Branch A renames `add` to `add_v2` and updates existing callers.
- Branch B independently adds a new caller of `add` in a new file.
- Each branch passes tests independently and their file changes do not overlap.
- The merged tree fails because Branch B retains the removed symbol.
