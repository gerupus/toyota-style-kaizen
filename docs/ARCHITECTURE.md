# Architecture: CEO-governed adaptive AI organization

**Human CEO** sets the mission, boundary conditions and significant decisions. **Logical COO** decomposes and prioritizes work (not necessarily an independent AI model). **Workers** execute by permitted host tools. **Quality gate** checks actual acceptance criteria; high-risk work requires the human and real host permission controls. **KAIZEN observer** reviews work-stream bottlenecks and unintended effects. **Independent challenger** tries to disprove the proposed optimization. **Learning layer** retains events and lessons with provenance.

The flow must be chosen from the task, not from an org chart: serial for dependency-heavy work, bounded parallel for independent research, and a single agent for trivial tasks. Spawn multiple agents only after measuring coordination costs.

## Two streams

1. **Value stream**: request → requirements → task DAG → work → evidence → review → delivery.
2. **Improvement stream**: observe → characterize issues → generate hypothesis → compare alternative (including do nothing) → bounded pilot → review harms → update standard *only by human or host-authorized procedure*.

Metrics: evidence-backed lead time, blocked queue size, review delay, rework count, quality defects, actual host-recorded cost and critical dependencies. The CLI currently computes task counts and observed cycle time only, and stores explicit measurements; it cannot measure unobserved host cost or subjective quality.

## Why no universal health 100-point score?

Numbers without grounded comparable definitions invite gaming. A declared evidence ID can be invented; a human-authored quality number can be biased. The ledger thus keeps **observed metrics separate from qualitative decisions** and avoids promoting process improvement on a composite index. Original Toyota systems and other firms' scoring schemes are referenced, but not claimed to be reproduced.

## Anti-pattern challenge

- More quality gates can worsen delivery time; use tests on review queue and escaped defects.
- Leaner WIP can improve throughput but reduce resilience; preserve slack for unpredictable API failures.
- More parallel agents can increase merge/rework time and duplicate research; compare with a single-worker baseline.
- Standards help reveal deviations yet can become rigid; reassess after context changes.
- Higher improvement count is not necessarily customer value. Deletion of an unnecessary improvement committee may be a genuine KAIZEN win.
