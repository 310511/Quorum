# Real-World Semantic Merge Dataset

Publication-quality benchmark mined from git history of six major Python projects.

## Quick start

```bash
source .venv/bin/activate
pip install -e .

# Full automated pipeline (phases 1–7) — clones repos; may take hours
real-world-pipeline run-all --repos requests --limit 500 --queue-limit 250

# Or phase-by-phase
real-world-pipeline mine --repos requests pydantic --since 2022-01-01
real-world-pipeline filter
real-world-pipeline detect
real-world-pipeline classify
real-world-pipeline heuristics
real-world-pipeline packages --limit 250
real-world-pipeline queue --limit 250

# Human review
real-world-pipeline serve --port 8765

# Export Quorum-evaluable pairs (required before `quorum eval`)
real-world-pipeline materialize

# Evaluate with Quorum (labels optional until human review completes)
python -m quorum eval dataset/real_world/examples --input-mode structured

# After annotation
real-world-pipeline agreement
real-world-pipeline freeze --require-agreement
real-world-pipeline materialize --only-annotated
```

## Layout

| Path | Phase | Description |
|------|-------|-------------|
| `real_world/miners/` | 1 | Clone repos, enumerate merge commits |
| `real_world/filters/` | 2 | Drop docs/tests/CI-only merges |
| `real_world/ast/` | 3 | AST symbol graph intersection |
| `real_world/analysis/` | 4,6,9,10 | Classify, heuristics, agreement, freeze |
| `real_world/review/` | 5,7,8 | Packages, CSV queue, web UI |
| `dataset/repos/` | — | Cloned upstream repositories |
| `dataset/real_world/` | — | JSONL artifacts + review queue |
| `dataset/real_world_candidates/` | 5 | Per-candidate packages |
| `dataset/real_world/examples/` | 10 | Frozen Quorum-compatible pairs |

## Quality rules

- **No LLM-generated labels** — heuristics produce `estimated_label` only
- **Human annotation required** for ground truth (`conflict` / `compatible`)
- Every example is reproducible from commit SHAs in `metadata.json`
- Target: ~200–250 examples, balanced ≈100 conflict / ≈100 compatible

## Repositories

- psf/requests
- pandas-dev/pandas
- pydantic/pydantic
- sqlalchemy/sqlalchemy
- fastapi/fastapi
- django/django

See `docs/REAL_WORLD_DATASET.md` for full protocol.
