# Operations: CEO-led local KAIZEN

## Source-of-truth contract

`.kaizen/events.jsonl` is canonical for CLI-recorded events. `.kaizen/board.json` and memory Markdown are materialized views. `charter.json` is a human-editable policy declaration, not a runtime policy engine. `.kaizen/` is ignored in Git by its nested `.gitignore`. Keep backups outside public repositories; do not store secrets.

The CLI has no AI API calls, no network access, no scheduler, no shell executor, no agent spawning, no authenticated identity and no deployment rights. The AI host performs work and can choose to invoke the skill's commands. A user must approve creating workspace files. A host is responsible for actual tool permissions, budget, isolation, external actions and CEO approval verification.

## First shift

From repo checkout: `python scripts/install.py --target /your/existing/project --agent codex --write-agent-guide --init --start --mission "CEO goal"`.

The one-time onboarding runs a bounded read-only file-name inventory (at most 2,000 files in counted set), records its time and outputs a T0001 task. Agent should read the charter + handoff, inspect actual content as permitted and record observations. T0001 may be completed with a written factual report **after** it is actually written and reviewed.

## Active task lifecycle

`add` → `task-start` (only dependencies done, under WIP and approval limits) → `memo`/work → `submit` (must include existing evidence file) → `review accept` (done) or `review rework` (todo) → next task. A blocked task may return to active once the blocker is addressed. High-risk task start requires a recorded CEO 'allow' and a high-risk review requires `--reviewer ceo` but neither is authenticated. Host must enforce all sensitive permissions, especially external write, publishing, deletion and spending.

### Example

```bash
python <skill>/scripts/kaizen.py add --workspace . --title "Map source paths" --acceptance "Report actual paths with sources" --risk low
python <skill>/scripts/kaizen.py task-start --workspace . --task T0002
python <skill>/scripts/kaizen.py memo --workspace . --category observation --task T0002 --text "Read these actual source files ..."
python <skill>/scripts/kaizen.py submit --workspace . --task T0002 --result "Source inventory completed" --evidence docs/report.md
python <skill>/scripts/kaizen.py review --workspace . --task T0002 --decision accept --reason "Report checked against actual files" --reviewer agent
python <skill>/scripts/kaizen.py next --workspace .
```

## Record measurements, not invented scores

```bash
python <skill>/scripts/kaizen.py measure --workspace . --metric end_to_end_seconds --value 62 --unit seconds --window baseline --sample-size 5 --method stopwatch --context coding_small_task --source tests/baseline.txt
python <skill>/scripts/kaizen.py measure --workspace . --metric end_to_end_seconds --value 47 --unit seconds --window trial --sample-size 5 --method stopwatch --context coding_small_task --source tests/trial.txt
python <skill>/scripts/kaizen.py compare --workspace . --metric end_to_end_seconds --before baseline --after trial --direction lower
```

These numbers are examples only. Comparing readings does not by itself demonstrate significance, causal effect, or absence of quality degradation. Record confounders, quality gates and negative impacts in memory before promotion. CLI v1.0 never changes global standards automatically.

## Escalation matrix

- Read-only analysis and local records in authorized workspace: agent may proceed after initial setup approval.
- Low-risk reversible project edits: subject to host permissions, task-specific quality checks and evidence.
- High-risk tasks, public pushes, payments, policy or permission changes, deleting user data, third-party communications: require CEO and host-enforced authorization. A JSON or text 'approval' alone is insufficient.
- Any unknown or unreviewable action: block and escalate, do not improvise elevated privilege.

## Organizational health without KPI theater

Status shows task count, measured cycle time of finished local tasks (and sample size), review queue, WIP and improvement proposal counts. It does **not** print arbitrary 100-point health ratings. The Toyota proposal point system and Toyota Engineering's separate GBM are historical inspiration, not exposed internal scoring. Missing measurements remain null; insufficient evidence is never silently assigned a best score.

## Failure recovery

Run `doctor`. If journal hash chain is valid but materialized board differs, use `doctor --repair` to reconstruct projections. If `events.jsonl` fails checksum or sequence validation, **stop all writes**; preserve files for manual investigation. If `.write.lock` remains after a crash, confirm no command is running and remove it yourself; no stale-lock removal by the AI. Tool execution in mid-command can leave a baseline or handoff without a start event: these pre-event files can be safely re-generated by invoking `start` again only if the organization has not started yet. Never delete or rewrite the authoritative journal to make tests pass.

## Operating cadence

After each completed task, record observations and at least one decision or explicit 'no change' decision. Do not force an improvement idea per task. Per user session, report exceptions, risk status, top bottleneck and pending CEO decisions. There is no background polling/notification; an external scheduler or the host agent must call the CLI on a later run.
