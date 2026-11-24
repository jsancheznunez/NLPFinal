---
name: git-workflow
description: "Branch, commit, open PRs, review and merge for this repo while keeping Netlify production deploys rare. Use for any git, PR or merge decision."
user-invocable: false
metadata:
  skill-id: S04
  shared-by: "orchestrator, solution-architect, netlify-engineer"
---

# Git workflow (branches, PR review, merging to main) (S04)

Shared by: `orchestrator`, `solution-architect`, `netlify-engineer`. Matrix: `docs/expert-roster.md` §3.

- GitHub flow: branch → commits → PR → review → merge → delete the branch (`knowledge/orchestrator/git-and-review-flow.md`).
- One task per branch, e.g. `feat/<area>-<thing>`. Each PR gets a **free** Netlify Deploy Preview, which is where QA tests.
- **Production deploys cost 15 credits each** (Free plan: 300/month). Merge to `main` at milestones, not for every change.
- Never force-push shared branches or rewrite history. Use `git merge --no-ff` (or squash) for feature merges.
- Merge gate: pytest green, schema validation green, Playwright green on the Deploy Preview, and the owner's definition of done met.
- Commit messages: imperative subject under 72 characters, body explaining why.
