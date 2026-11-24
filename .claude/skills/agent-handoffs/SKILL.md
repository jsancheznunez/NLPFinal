---
name: agent-handoffs
description: "Write self-contained delegation prompts and handoff notes between the analyzer's agents. Use when delegating to a subagent, writing an agent or skill file, or passing work from one agent to the next."
user-invocable: false
metadata:
  skill-id: S03
  shared-by: "orchestrator, meta-agent, solution-architect"
---

# Agent prompt & handoff design (S03)

Shared by: `orchestrator`, `meta-agent`, `solution-architect`. Matrix: `docs/expert-roster.md` §3.

- A subagent starts with a **fresh context**. It sees only its system prompt, your task message, CLAUDE.md, git status, its preloaded skills and the injected knowledge INDEX (`knowledge/orchestrator/delegating-to-subagents.md`).
- Every handoff states:
  1. the goal, in one sentence
  2. input files and schemas
  3. output paths
  4. constraints from `project-constraints`
  5. the definition of done
  6. what to return (a short summary plus how it was verified)
- Name the receiving agent explicitly (`Use the spacy-expert subagent to…`). Ask for **short summaries** back.
- Don't paste large files into prompts. Reference them by path.
- Record the decisions that cross agents (interfaces, pins) in the repo (docs/ or schemas/), not only in chat.
