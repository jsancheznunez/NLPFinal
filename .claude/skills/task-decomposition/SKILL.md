---
name: task-decomposition
description: "Break the analyzer project into dependency-ordered tasks with owners and definitions of done. Use when planning work, sequencing agents, or deciding what can run in parallel."
user-invocable: false
metadata:
  skill-id: S01
  shared-by: "orchestrator, meta-agent"
---

# Task decomposition & dependency planning (S01)

Shared by: `orchestrator`, `meta-agent`. Matrix: `docs/expert-roster.md` §3.

- Start from the dependency order in `knowledge/orchestrator/project-plan.md`: design → data → NLP layers → metrics → pipeline → web → deploy → test → deliver.
- Each task names **one owner**, its inputs (files or schemas), its outputs (exact paths), and a definition of done that can be checked.
- Run tasks in parallel only when they share no files and only meet at a frozen interface (e.g. spaCy and NLTK layers against `tests/fixtures/`).
- Keep each task small enough for one PR with one Netlify Deploy Preview.
- Re-plan when a gate fails. Don't let downstream agents build on unvalidated output.
