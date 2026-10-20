# Adversarial analysis: failures of KAIZEN and failures of AI organizations

Do not treat every conventional lean practice as a universal good. Each suspicious KPI or intervention must have an explicit counterfactual test.

| Apparent good | Hidden loss | Observation / falsification | Countermove |
|---|---|---|---|
| Many improvement ideas | Paper ideas, incentive gaming | acceptance rate, downstream effect, repeatability, effort vs outcomes | remove proposal quotas and compare net effect |
| Higher agent utilization | queue overload, user wait | p50/p95 waits, WIP, errors vs actual accepted deliveries | lower WIP or add reserve |
| Faster worker | rework moves downstream | whole-job lead and escaped defects | optimize system critical path |
| More specialized agents | duplicated search, handoff defects | same benchmark against 1-agent baseline | merge roles |
| More inspection and Andon | false holds, CEO inbox flooding | alert precision, stalled time, approvals | risk-tier and cut low-value reviews |
| More standards | rigid prompt overfitting | holdout tasks, novel task quality, escaped anomalies | bounded exceptions and shadow exploration |
| JIT / no buffers | fragile supplier/API outage | incident recovery and alternative supplier tests | retain buffer/cache/fallback |
| More autonomous approval | unauthorized write | approval audit, role-gate adversarial tests | real enforcement in runtime, human signoff |
| Higher numerical grade | evaluator gaming, missing denominators | cross-slice/hard gate evaluation, independent evidence | show raw metrics, thresholds and missing data |
| More KAIZEN actions | self-referential process overhead | time and tokens spent on audits vs accepted value | NO_CHANGE/REMOVE_AUDIT |

**Hostile cases to evaluate:** fabricated scoring evidence; skill claims ability to spawn agents when host cannot; CEO instruction conflicts with a critical safety gate; manager tries to approve its own irreversible patch; one model plays both producer and independent judge; proposed 'cost saving' removes vital review; a fail-forward workaround retries a denied action through another agent; a score improves after trivial tasks are selected.

**Independent evaluator principle:** different roles are insufficient; require separate tests, alternative datasets, policy constraints, or explicit human validation where possible.
