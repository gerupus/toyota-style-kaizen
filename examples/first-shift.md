# First shift: worked-through example (illustrative, not benchmark data)

1. Download this repo and prepare an **existing test project**.
2. `python scripts/install.py --target /path/to/test-project --agent codex --init --start --mission "Reduce reproducible docs regressions"`
3. Check `.kaizen/charter.json`, `.kaizen/handoffs/T0001.md`, `.kaizen/baseline/startup-inventory.json`. The inventory counts files; it does not inspect code contents.
4. Ask Codex to read installed `toyota-style-kaizen` skill, then analyze actual project docs and record observations. The agent must use permitted file tools and call the `memo` command, not merely claim that it kept notes.
5. Write a real report to `docs/current-state.md` in the target project. The agent submits T0001 only after creating the file, then a reviewer verifies the claims and records an accept/rework judgment.
6. Create T0002 with explicit acceptance criterion and dependency on T0001. Demonstrate that T0002 cannot start until T0001 is accepted.
7. To compare a process change, collect real before/after measurements with equivalent method, unit and context; record external sources inside the project. `compare` reports *observed difference*, not improvement proven.
8. Run `doctor` and `report --write` and end with a CEO summary: delivered value, unverified claims, outstanding risks, pending approvals, total coordination overhead and a recommended next action.

**Failure drills**: forge a data path, set a false CEO reviewer, damage `board.json`, and damage `events.jsonl`. The expected outcomes differ: nonexistent evidence is rejected; forged CEO flag is *not* authenticated and therefore must be rejected by host policy; projection repair is permitted; journal corruption fails closed.
