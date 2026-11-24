# CLAUDE.md and instruction design

Sources:
- https://code.claude.com/docs/en/memory.md
- https://code.claude.com/docs/en/best-practices.md

- CLAUDE.md loads into every session **and into every subagent** ("every level of the CLAUDE.md hierarchy the main conversation loads").
- "**Size**: target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence." Put part-of-codebase rules in `.claude/rules/` with `paths`.
- "if two instructions contradict each other, Claude may pick one arbitrarily". Review periodically.
- Imports: `@path/to/import` expands a file into context. Paths inside backticks or code blocks are *not* imported. Don't import large knowledge files into CLAUDE.md; link them instead.
- "Claude treats CLAUDE.md files and auto memory as context. They aren't enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook."
- Best practices, deterministic vs non-deterministic: prompts, CLAUDE.md and skills are read by the model ("Claude decides"). Hooks, deny rules and managed settings are applied by Claude Code every time. ⇒ Here, "read your knowledge folder" is **enforced by a SubagentStart hook** (deterministic injection of the INDEX) **and** stated in each agent prompt (non-deterministic instruction to read the relevant files).
