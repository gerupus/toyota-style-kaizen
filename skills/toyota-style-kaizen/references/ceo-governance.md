# CEO governance: a small AI organization that can learn

**Human CEO** owns purpose, required acceptance criteria, permissible data sources, budget, restrictions and all high-impact decisions. The AI manager has delegated planning authority, not unlimited permission. Every instruction is bounded by host permissions.

## Structure selected by need, not an office-chart ritual

1. **CEO** defines a goal in `.kaizen/charter.json`, identifies forbidden actions and determines what needs approval.
2. **Flow coordinator (COO role)** observes the current state in `board.json`, translates the goal into acceptance-based tasks, schedules DAG dependencies and WIP with the installed CLI.
3. **Workers** execute allowed activities; use a single worker by default. Introduce specialist roles or parallel workers only if independent subproblems and reliable handoffs justify them.
4. **Quality gate** checks actual evidence before marking a task done, using `submit` and `review` transitions. Host-level approval must be real for restricted writes.
5. **KAIZEN observer** checks waiting, review queues, rework, total flow, defects, API fragility and coordination overhead. It proposes reversible pilots and records contrary outcomes.
6. **Independent challenger** examines a different data slice, test result or counter-hypothesis. Two role labels on the same unsupported assumption do not equal independent evidence.
7. **Learning ledger** records facts, decisions, lessons, risks and measured comparisons. Unproven improvements may be tested but are not silently promoted.

## CEO policy and authority

By default `init` creates a charter with WIP=2 and a local record-only policy. The operator may edit the charter after understanding the implications. The CLI validates WIP range but **cannot enforce real network permissions**; the host must require authenticated human approval for external write, publishing, payments, secrets, deletion, credential updates and system policy changes. A task approval record is only an attestation, not identity proof.

## Daily process / Obeya adaptation

For each work session, report mission, active work, blocked queue, tested outcomes, unverified assumptions, host-reported spend if available and pending CEO decisions. Avoid inventing cost or throughput. If the KPI is unmeasured, say so.

Use `memo` for important facts and decisions. Use `measure` for comparable quantitative evidence and `compare` for descriptive differences only. Use `improve` to log hypotheses. There is no automatic stage called 'proven' or 'promoted' in v1.0.0: this is intentional to prevent gaming and premature standardization.

## Improvement of the improvement organization

Review audit overhead and alert false positives. If increased management and reporting time outweigh the benefits, simplify the organization. 'No change' and 'remove unnecessary audit' are legitimate outcomes. Do not turn Toyota terminology into compulsory meetings or fixed 5 Whys rituals.

Operational steps: [`OPERATIONS.md`](OPERATIONS.md) (also available as `references/OPERATIONS.md` from the skill root). Repo-wide explanation: `docs/ARCHITECTURE.md` is informative for repository readers, but the installed Skill remains self-contained when it is not accessible.
