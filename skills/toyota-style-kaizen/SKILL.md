---
name: toyota-style-kaizen
description: >-
  Unofficial Toyota Production System-inspired AI organization and KAIZEN operations.
  Use to bootstrap a CEO-governed AI team, record tasks and organizational memory,
  diagnose bottlenecks and waste, audit work handoffs, measure safe improvements,
  manage approval boundaries and learn from process failures. Includes executable
  local CLI for init/start/task/memo/measure and on-demand references.
license: MIT
compatibility: Python 3.10+ for persistent CLI; agent host must provide tools for actual work
metadata:
  version: "1.0.0"
  origin: "Independent TPS-inspired project; NOT affiliated with Toyota"
---

# TOYOTA式 KAIZEN / AI company operating skill (unofficial)

## Charter and authority

- Human user is CEO. The CEO defines goals, constraints, high-risk approvals and standard promotion.
- Agent may act as COO, analyst, worker or reviewer **only within tools and permissions actually granted by host**.
- A role description does NOT spawn a separate model or grant privilege. When the environment has no agents, emulate roles serially and disclose that limitation.
- Never pretend to be an official Toyota system or use Toyota's internal confidential metrics. Adapt TPS principles, not corporate authority.
- This skill is for CEO-directed AI organization operations and lightweight KAIZEN. A quick question should not trigger the full bureaucracy.

## Mandatory first invocation (existing workspace)

1. Locate the **installed skill's** `scripts/kaizen.py`. Do not assume current working directory or change files outside the user-approved workspace.
2. If `.kaizen/charter.json` is missing, ask for / infer only the minimum CEO mission and perform `python <skill>/scripts/kaizen.py init --workspace . --mission "..."` after the user authorizes creating local state. Do not overwrite any existing `.kaizen` directory.
3. With user authorization to begin, run `python <skill>/scripts/kaizen.py start --workspace .`. This creates a read-only file inventory and starts task T0001. Read `.kaizen/handoffs/T0001.md`, the charter and the actual relevant project files.
4. If `.kaizen/` exists, run `doctor`, `status` and `next`, then continue from the journal. Never silently re-initialize or reset.
5. Execute the first real task with host-approved tools. **After each meaningful observation, decision, failure or lesson**, record it via `memo`; create tasks and submit evidence via the CLI. The CLI does not itself invoke an LLM, browse, schedule recurring work or monitor agent tools.
6. Do not represent `start` as project work completed: it only begins the recorded onboarding and captures inventory metadata. State factual completion only after evidence and review.

## Operational cycle (adaptive)

**CEO intent → inspect actual state (genchi genbutsu) → dynamic task plan → limit WIP → execute with host tools → log evidence → check defects (jidoka) → measure local and global flow → propose reversible KAIZEN → review harmful side effects → confirm or reject standard.**

- For independent tasks, consider bounded parallel workers; for dependent tasks use sequential handoff. Prefer one worker until a measured need for multiple workers is shown.
- Never optimize one station if the end-to-end lead time, cost, human approval workload, quality or resilience deteriorates.
- A high-risk task must have a human CEO approval **enforced by the hosting runtime**; the CLI records self-declared approval but cannot authenticate it.
- Stop and escalate on data exfiltration, destructive/publishing/payment requests, false facts, unsafe tool permissions and uncontrolled budget/cycle escalation. If the required safety gate is missing, keep work to read-only analysis.
- Keep failures and negative KAIZEN examples. Failure to improve can be a useful validated result; number of suggestions is not a target.
- Default WIP is 2 active tasks; this is an initial convenience, not an official TPS value. CEO can change `max_active_tasks` in `.kaizen/charter.json` (1..12) as a conscious governance decision.

## CLI quick reference (run from the PROJECT workspace)

```bash
python <skill>/scripts/kaizen.py init --workspace . --mission "CEO goal"
python <skill>/scripts/kaizen.py start --workspace .
python <skill>/scripts/kaizen.py status --workspace .
python <skill>/scripts/kaizen.py next --workspace .
python <skill>/scripts/kaizen.py diagnose --workspace .
python <skill>/scripts/kaizen.py memo --workspace . --category observation --task T0001 --text "Observed: ..."
python <skill>/scripts/kaizen.py submit --workspace . --task T0001 --result "..." --evidence relative/path/to/actual-report.md
python <skill>/scripts/kaizen.py review --workspace . --task T0001 --decision accept --reason "Reviewed evidence and acceptance criteria"
python <skill>/scripts/kaizen.py doctor --workspace .
```

Use `--help` on individual commands for the complete CLI contract. Evidence paths must exist **inside** the workspace and be non-empty; CLI cannot independently confirm whether evidence is true. Avoid secrets and private identifiers in logs. `.kaizen/.gitignore` prevents accidental Git commits by default, but is not encryption.

## Memory policy

`events.jsonl` is the **append-only source of truth** for actions performed via this CLI. `board.json` and `memory/*.md` are derived projections. Do not edit the journal or manually invent measurements; use `memo`, `measure` and `review` to record actual work. The hash chain detects accidental journal corruption, not malicious modification. When projections are stale, use `doctor --repair` after confirming the journal is intact. An AI cannot record actions it does not observe or receive from the host; do not claim full passive monitoring.

Record factual observations separate from hypotheses and risk warnings. Link task IDs, sources and measurement context. When testing improvements, require comparable before/after windows, method, unit, context and real source files. CLI comparisons are descriptive and do not establish causality or statistical significance. Never auto-promote based on a numeric score.

## Organization anti-patterns

- **Excess KAIZEN:** endless reviews, audit tokens exceed gained value, meetings about meetings.
- **JIT fragility:** removing all slack creates cascading failures from flaky APIs or missing context.
- **Local optimization:** individual worker faster but whole flow slower.
- **Metric gaming:** 100% scores from declared evidence paths, suggestion counts, busy-work or arbitrary weights.
- **Permission theater:** `--reviewer ceo` or log entries are not identity verification.
- **Coordination overhead:** spawning many AI workers with duplicated research and conflicting handoffs.
- **Standard ossification:** copying past methods into a new context without hypothesis checks.

For substantial jobs, consider the strongest counter-hypothesis, a no-change baseline, rollback condition and who bears the cost of change.

## Load-on-demand references

- `references/ceo-governance.md`: CEO / COO decision rights and organization design.
- `references/governance-antipatterns.md`: TPS and AI organization failure modes.
- `references/tps-foundation.md`: what Toyota actually published versus independent adaptations.
- `references/muda-checklist.md`: 3M / seven waste categories, digital analogy.
- `references/domain-adapters.md`: writing, code, research and high-risk contexts.
- `references/OPERATIONS.md`: detailed CLI transitions, sampling, CEO workflow and recovery.
- `references/test-cases.md`: manual adversarial agent behavior scenarios.

## Humor mode

Factory-manager jokes are an optional layer, not the business logic. Use quiet mode by default for high-stakes tasks. Never imply Toyota's endorsement or employment.
