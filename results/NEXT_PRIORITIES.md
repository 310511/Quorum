# Quorum next-step roadmap (post leakage-free eval)

## Status

**Adjudicator v3 is FROZEN** (behavior-break gate).
See `results/adjudicator_v3_verification.md`.

Offline (identical model outputs, new adjudication only):
- Blind 200: Acc 44% → **99%**, Spec 0% → **100%**, MCC −0.25 → **0.98**
- Hard negatives: Acc 83% → **92%**
- Compatible twins (partial): Acc ~35% → **100%** Spec

Do **not** modify `quorum/adjudicate_v2.py` until after:
1. Full re-eval with frozen v3
2. Evaluation chapter draft
3. Independent leakage / implementation audit

---

## Priority 1 — Mistake catalog ✅

`results/error_analysis.md`, `error_catalog.json`, `error_catalog.csv`

## Priority 2–3 — Behavior-break gate + evidence scoring ✅ (frozen)

## Next (in order)

4. Human annotation (~50 pairs, dual review)
5. Real-world PR/merge dataset (≥100)
6. Benchmark documentation
7. Full baseline comparison table on frozen v3

## Explicitly defer

- further adjudicator tweaks
- more synthetic mutations
- more committee members
- prompt churn
