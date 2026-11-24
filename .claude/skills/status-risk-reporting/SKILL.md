---
name: status-risk-reporting
description: "Report progress, blockers and risks concisely and honestly. Use at the end of every task, at milestones, and whenever something is blocked or deviates from plan."
user-invocable: false
metadata:
  skill-id: S21
  shared-by: "orchestrator, meta-agent, netlify-engineer"
---

# Status reporting & risk tracking (S21)

Shared by: `orchestrator`, `meta-agent`, `netlify-engineer`. Matrix: `docs/expert-roster.md` §3.

Status format (keep it short):
- **Done:** what changed (paths) and how it was verified (command plus result).
- **Not done / skipped:** what, and why.
- **Risks:** e.g. build time near budget, credit usage, a version-pin mismatch, Pyodide cold-load time, dataset license.
- **Next:** the owner and the next step.
Never report something as done without evidence. Report failures with the actual output.
Track standing risks in `docs/risks.md` (create it if missing): risk, likelihood, impact, mitigation, owner.
