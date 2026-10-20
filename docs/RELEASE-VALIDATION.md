# Public v1.0.0 release validation (2026-10-20)

## Automated test coverage

Run `python -m unittest discover -s tests -v` from repo root.

Locally tested with Python 3.13 on Linux in an isolated temporary workspace:

- Initialize and refuse existing state; start read-only inventory and T0001; resume journal.
- Install portable skill into Codex and Claude project directories; opt-in AGENTS.md and CLAUDE.md; refuse overwrite.
- Record memo and local event transition; maintain DAG prerequisite and WIP limits; block/restart and rework.
- Validate evidence stays inside project, exists and is non-empty. These checks are **not** truth verification.
- Record CEO decision for high-risk task; require review attestation; do **not** claim authentication.
- Disallow automatic promotion; detect missing measurements, verify comparable measurement windows/context/method.
- Flag workflow bottleneck signals and observed positive signals without pseudo-exact organization scores.
- Detect corrupt journal and fail closed; rebuild derived state; refuse symlinked memory output and stale write lock.
- Verify bundled entrypoint, references, JSON templates, docs and license.

## Host integration test not yet performed

- No end-to-end agent model run was performed on a user's actual repository.
- Real Codex/Claude Code skill auto-discovery and correctness in the user environment are not measured.
- Automated authentic CEO approvals, spending limits, multi-agent spawning and background schedules are not included.
- Windows matrix is configured in GitHub Actions, but unexecuted until repository publication enables CI.

This artifact is a tested local operating toolkit with an agent-facing skill, not a production-grade autonomous organization platform.
