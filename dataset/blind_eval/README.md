# Blind two-branch evaluation pack

Model-visible inputs live under `pairs/<id>/`:
- `left.diff`
- `right.diff`
- optional `base/` checkout at merge-base
- `meta.json` with no labels

Do **not** provide `labels.sealed.jsonl` to the model.
It is for scoring only.
