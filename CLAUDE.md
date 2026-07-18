# Quorum — Project Memory

This file gives Claude Code full context on the Quorum project. Load this automatically at the start of every session in this repo.

## Course context
- Course: BCSE301L — Software Engineering
- Faculty: Elakiya E
- Institution: VIT, School of Science and Engineering
- Deliverable so far: an SRS document (v1.0) submitted as a DA

## One-line description
Quorum is a heterogeneous LLM committee that catches the semantic merge conflicts AI coding agents can't see.

## The problem
AI coding agents (Claude Code, Cursor, Codex, Gemini CLI) increasingly work in parallel on the same repo. Git's conflict detection only catches textual overlaps — two agents editing the same lines. It misses semantic conflicts: independently-authored branches with zero line-level overlap that are still logically incompatible (e.g. Agent A renames a function, Agent B's branch still calls it by the old name).

## Evidence the problem is real and unsolved
- **CooperBench** (Stanford/SAP Labs, arXiv 2601.13295): frontier models (GPT-5, Claude Sonnet 4.5) achieve only ~25% success on cooperative coding tasks — roughly 50% lower than one agent doing both tasks alone. Agents make unverifiable claims about code state, ignore agreed integration points, break commitments, and hold incorrect assumptions about their partner's plans. Called the "curse of coordination."
- **AgenticFlict** (arXiv 2604.03551): the first dataset of AI-agent-authored merge conflicts (142K+ agentic PRs, 59K+ repos, 27.67% conflict rate). Explicitly textual-only — the authors name semantic/logical conflict detection as unaddressed future work.
- Reviewed adjacent prior art and ruled out direct overlap: **MAGIS** (arXiv 2403.17927, single-model simulated dev team, closes one GitHub issue at a time, no persistence), **GitHub Agent HQ** (multi-vendor orchestration + "Blackboard" shared state + human arbitration, but reactive/human-arbitrated, not an automated semantic checker, and deeply tied to GitHub/Copilot), **OpenClaw** (personal assistant gateway, agents isolated per-channel, never share a workspace so never need conflict detection).

## The approach: a committee, not a single model
Instead of one model (or the same agent auditing its own work — same-model self-audit shares blind spots), run each proposed code change through a **committee of structurally different LLMs** (e.g. Claude, GPT, Gemini, or locally via Ollama). Each model returns a verdict **with a reasoning trace**, not just yes/no — plain majority voting can converge confidently on a shared wrong answer when models share failure modes, so disagreement is adjudicated on evidence, not tallied. Unresolved cases escalate to a human reviewer within a time budget.

This borrows the ensemble-diversity principle from ML (differently-trained models fail in decorrelated ways) and applies it specifically to semantic conflict detection between AI-agent-authored branches — a combination not found published or shipped elsewhere as of this writing. Background: **Mixture-of-Agents** (arXiv 2406.04692) shows heterogeneous LLM ensembles beating GPT-4 Omni on AlpacaEval (65.1% vs 57.5%).

## Five-layer architecture
1. **Data layer** — labeled dataset of agent-vs-agent semantic conflicts (compatible / textual conflict / semantic conflict), sourced from CooperBench, AgenticFlict, and self-generated agent runs. This is the project's real moat — harder to copy than the code.
2. **Ingestion layer** — git hooks/webhooks watch for concurrent agent branches, queue diff pairs for analysis. MVP shortcut: a manually-invoked CLI (`quorum check branch-a branch-b`) instead of full webhook infra.
3. **Semantic extraction** — Tree-sitter AST parsing + call-graph/dependency delta per branch relative to merge-base. Turns raw diffs into structured JSON (functions changed, call sites affected, signatures changed) fed to the committee — not raw diffs.
4. **Committee layer** — N heterogeneous models vote with reasoning traces; evidence-based adjudication (not tally voting); time-boxed, parallel calls.
5. **Arbitration layer** — human review UI / PR-comment bot for escalated disagreements.

## Local-first prototype strategy (current decision)
Phase 0/1 runs entirely on **Ollama** (open-weight models, local, zero API cost) rather than paid hosted APIs, for two reasons:
- Keeps the academic prototype at zero marginal cost until the core hypothesis is validated.
- Ollama makes it easy to run several architecturally distinct open-weight families side by side (e.g. Qwen-Coder, DeepSeek, Llama, GLM) — genuine diversity for the committee, arguably more decorrelated than Claude+GPT+Gemini alone.

Tradeoff accepted explicitly: local open-weight models trail frontier APIs on complex reasoning, so Phase 0/1 results are a **lower bound**, not a ceiling, on committee performance.

Migration path: Ollama exposes an OpenAI-compatible REST API. The committee orchestration layer must be written against a generic `{endpoint, model_name}` interface so a local Ollama model and a hosted API model (Anthropic/OpenAI/Google) are interchangeable via config only — no code changes. (This is FR-11 / NFR-4 in the SRS.)

Hardware note: works fine on an M2 MacBook. 8GB unified memory is tight (small models only, sequential calls). 16GB is the realistic sweet spot for Phase 0 (mid-sized coder model, sequential committee calls). 32GB+ allows genuinely parallel calls toward the eventual <2min time budget.

## Phased build plan
- **Phase 0 (2–4 weeks):** CLI tool, manual invocation, 2–3 local models via Ollama, raw diffs fed to models. Test against 15–20 hand-picked CooperBench conflict pairs, single model vs. committee. **Status: prototype done; full eval set pending.**
- **Phase 1 (4–8 weeks):** Tree-sitter Python function-level delta (no call-graph yet); re-test same pairs, measure lift from structured input vs raw diff. **Status: AST extraction layer done; awaiting full comparison eval.**
- **Phase 2 (4–6 weeks):** data + evaluation rigor — labeling tool, 300–500 labeled examples, real precision/recall against full CooperBench set.
- **Phase 3 (6–8 weeks):** productionize — webhook ingestion, GitHub PR bot, human review UI, cost/time budgets, observability (Langfuse/Helicone).
- **Phase 4:** distribution decision — GitHub Action/CI check vs. standalone SaaS vs. plugin into Agent HQ.

## Phase 0 results (preliminary)
Hardware: M2 MacBook Air, 8 GB RAM. Models: `gemma4:e2b`, `qwen2.5-coder:3b` (committee sequential, 300s per-call timeout).

| Metric | Value | Notes |
|--------|-------|-------|
| Labeled pairs tested | 1 (`example_1`) | Full 15–20 pair set not yet created |
| Raw baseline accuracy | 0/1 | Missed on later re-run (model non-determinism) |
| Raw committee accuracy | 0/1 | Escalated (split verdict) |
| Structured baseline accuracy | 1/1 | Correctly flagged `conflict` |
| Structured committee accuracy | 0/1 | Escalated — gemma4:e2b said compatible, qwen2.5-coder:3b said conflict |

`example_1` (function rename + stale import): structured input helped the baseline see the rename conflict; committee still escalated because gemma4:e2b did not connect branch_b's `calculate_total` usage to branch_a's rename. This justified adding import/call-site hints to the structured delta (still no full call-graph).

## Phase 1 status
- **Done:** Tree-sitter Python extraction, function delta + `cross_branch_links`, structured prompts, CooperBench import (`python -m quorum import-cooperbench`).
- **Dataset:** 20 CooperBench pairs imported under `data/pairs/` (16 Python, 2 Go, 1 TypeScript, 1 Rust) + `example_1`. Labels: 12 conflict, 8 compatible (clean_merge).
- **Not built yet:** full call-graph, multi-language AST, Neo4j/Kuzu.
- **Next step:** `python -m quorum eval --compare-inputs data/pairs` (structured runs Python pairs only; raw runs all 21).

## Explicit judgment calls (don't relitigate these without new evidence)
- **Not competing with GitHub Agent HQ on infrastructure.** Quorum is a narrow, deep detection capability that could plug into Agent HQ, GitLab, or standalone CI — not a full orchestration platform.
- **False positives are the bigger adoption risk than missed conflicts.** Bias detection conservative early; tune aggressiveness up only as precision data comes in.
- **Same-model committees don't count as diverse.** Verify chosen models actually diverge in failure modes on the eval set before building voting infra around them.
- **Don't build the dataset before validating the hypothesis.** 15–20 labeled examples is enough for Phase 0; 500 comes later (Phase 2), not now.

## Tech stack reference (for later phases)
- AST/call-graph: Tree-sitter, ts-morph (JS/TS), jedi/rope (Python), Sourcegraph SCIP / stack-graphs (cross-language)
- Graph storage: Neo4j or Kuzu (embedded)
- Orchestration: LangGraph (preferred for explicit voting/escalation state machine) or a thin custom async orchestrator
- Backend: Python (FastAPI) — leans on the AST/graph tooling ecosystem
- Observability: Langfuse or Helicone for LLM call tracing/cost
- Deployment: Docker → Fly.io/Railway for v0

## Naming
Project name: **Quorum** (shortlisted after "Canopy" had naming conflicts with existing products).

## Key references
- CooperBench — https://arxiv.org/abs/2601.13295
- AgenticFlict — https://arxiv.org/abs/2604.03551
- GitHub Agent HQ announcement — https://github.blog/news-insights/company-news/welcome-home-agents/
- MAGIS — https://arxiv.org/abs/2403.17927
- Mixture-of-Agents — https://arxiv.org/abs/2406.04692
- Ollama model library — https://ollama.com/library

## Open items / not yet decided
- Exact Ollama model pairing for Phase 0 (depends on final hardware — confirm RAM before picking models; check `ollama.com/library` for current tags, the lineup shifts monthly)
- Whether to pursue a provisional patent filing (likely not patentable as a bare ensemble-voting mechanism; possibly defensible as the specific application + resulting dataset — discuss with a specialist IP attorney once a working prototype exists, not before)
- Registration/ID number for the SRS cover page (currently just "Utsav Gautam", no reg. no. filled in)
