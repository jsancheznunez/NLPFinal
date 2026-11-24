# Skill files

Source: https://code.claude.com/docs/en/skills.md

- Location: `.claude/skills/<skill-name>/SKILL.md`. "The directory name, or the frontmatter `name` when you set one, becomes the command you type, and the `description` helps Claude decide when to load the skill automatically."
- Frontmatter uses lowercase hyphenated names. "All fields are optional. Only `description` is recommended." Unknown fields are ignored silently.
- Key fields:
  - `name`
  - `description`: "Put the key use case first". The combined `description` + `when_to_use` is truncated at 1,536 characters in the listing.
  - `when_to_use`
  - `user-invocable` (`false` = "Only Claude can invoke the skill... Use for background knowledge users shouldn't invoke directly")
  - `disable-model-invocation` (`true` blocks auto-loading **and** preloading into subagents)
  - `allowed-tools`, `model`, `effort`, `context: fork` + `agent`, `paths`, `metadata`
- **Types of content:** "Reference content adds knowledge Claude applies to your current work. Conventions, patterns, style guides, domain knowledge." "Task content gives Claude step-by-step instructions for a specific action." Our 24 skills are reference content. Deploy-type actions would use `disable-model-invocation: true`.
- "Keep the body itself concise. Once a skill loads, its content stays in context across turns, so every line is a recurring token cost." "Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files", and reference them from SKILL.md so Claude knows when to load them. In this repo the detailed material lives in `knowledge/<agent>/`.
- Lifecycle: invoked content "enters the conversation as a single message and stays there across later turns". After compaction, Claude Code re-attaches up to 5,000 tokens per skill within a 25,000-token shared budget.
- To use the Agent Skills spec outside Claude Code, only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools` are allowed. Our skills use `user-invocable`, which is Claude Code-only, so don't upload them to claude.ai unchanged.
