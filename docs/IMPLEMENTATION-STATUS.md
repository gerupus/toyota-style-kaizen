# v1.0.0 implementation status

## Implemented and tested locally

- Vendor-neutral Agent Skills `SKILL.md` and all referenced guidance packaged together.
- Opt-in installer for project-local Codex `.agents/skills` and/or Claude `.claude/skills`.
- `init` provisions `.kaizen/` without overwriting existing state. Local state excluded from Git by default.
- `start` records an actual **read-only filename inventory**, persists an initial handoff, and opens first task T0001. It does not execute that task's substantive AI work.
- Durable local event ledger (JSONL, fsync) with per-event SHA-256 hash linking and optimistic concurrency guard + a simple exclusive write lock.
- Projections (`board.json`, Markdown memory) regenerated from events. `doctor` and explicit projection repair.
- Task dependencies, WIP cap, evidence-file checks, submit/review/rework, high-risk approval records.
- Improvement proposals, non-automatic trial decisions, measurement source paths, descriptive before/after comparison with context/method checks.
- Automated Python standard-library tests and CI workflow.

## Not provided (must not claim as operational)

- Authenticating the person supplying CEO approval: CLI `approve` / `--reviewer ceo` are **attestations**, not signed authorization.
- Model execution, autonomous orchestration, AI agent spawning, auto-delegation, token/cost metering, any scheduler, cross-session background processing, third-party sync or notifications.
- Complete event capture from unrelated agent activities (agents must run the CLI or the host must integrate event hooks).
- External permissions / sandbox enforcement / billing restrictions / network isolation: delegated to host runtime.
- Automated truth verification of evidence files, causal inference, significance testing, or final quality assurance.
- Safe automatic application/promotion of improvements or software rollbacks.
- End-to-end real-model tests in Codex and Claude Code on real customer projects.

## Release criteria and boundaries

The phrase 'operational v1.0.0' refers to a tested **local setup, memory and workflow ledger** that an AI host can drive. It is NOT a complete autonomous AI enterprise product. A subsequent release requires a provider-specific execution adapter, authenticated approvals, resource budgets, consistent event hooks and real-model E2E trials before such a claim is warranted.
