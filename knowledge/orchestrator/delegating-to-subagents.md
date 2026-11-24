# Delegating to subagents (Claude Code)

Sources:
- https://code.claude.com/docs/en/sub-agents.md
- https://code.claude.com/docs/en/best-practices.md
- https://code.claude.com/docs/en/agent-teams.md

## What a subagent starts with
- "Each subagent starts with a fresh, isolated context window. It doesn't see your conversation history, the skills you've already invoked, or the files Claude has already read." It receives:
  - its own system prompt (the agent file body)
  - **the task message you write**
  - CLAUDE.md files
  - a git status snapshot
  - preloaded skills (the `skills` field)
  - a sibling roster if it has `SendMessage`
- ⇒ **Every delegation prompt must be self-contained.** Include the goal, the files to touch, the interface or schema to follow, the definition of done, and what to return.
- In this repo, a `SubagentStart` hook (`.claude/settings.json`) injects the agent's `knowledge/<name>/INDEX.md` automatically.

## Invoking
- Claude Code delegates automatically "based on the task description in your request, the `description` field in subagent configurations, and current context."
- To invoke explicitly: name the agent ("Use the spacy-expert subagent to …"), @-mention it (`@agent-spacy-expert`), or run a whole session as one agent with `claude --agent orchestrator`.

## Foreground vs background
- "With nothing configured, a subagent... that Claude spawns from your main conversation starts in the background." Background subagents keep `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write`, `WebFetch`, `WebSearch`, `Skill`, `SendMessage` and MCP tools, but lose `AskUserQuestion`, plan mode and others. Their permission prompts surface in the main session.
- "A background subagent's results reach Claude as a completion notification in a later turn." Don't guess results before the notification arrives.

## Patterns
- **Isolate high-volume operations**, such as test runs and doc fetching, so only a summary comes back.
- **Run parallel research** for independent pieces. Warning from the docs: "Running many subagents that each return detailed results can consume significant context." Ask for short summaries.
- **Chain subagents**: "Each subagent completes its task and returns results to Claude, which then passes relevant context to the next subagent." This is the build order in project-plan.md.
- **Nesting**: "a subagent can spawn subagents of its own, up to three layers below the main conversation". The default can be changed with `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`.

## When not to delegate (docs)
Use the main conversation when "The task needs frequent back-and-forth", when "Multiple phases share significant context", for "a quick, targeted change", or when "Latency matters".

## Cost (best-practices)
- "every subagent sends its own requests and they count against the same usage." A fresh subagent "can end up *slower*" because it has to gather context again. "You get parallelism or a fresh pair of eyes out of it, but not a smarter answer."
- "Set `model: haiku`... if its work is simple." "Ask for short summaries back."

## Agent teams vs subagents
- "Use subagents when you need quick, focused workers that report back. Use agent teams when teammates need to share findings, challenge each other, and coordinate on their own." Agent teams "use significantly more tokens". **This project uses subagents coordinated by the orchestrator.**

## Observed in this project (Nov 24 2026)
- When the orchestrator itself runs **as a subagent**, its tool list may not include the Agent/Task tool, even though the docs allow nesting ("up to three layers below the main conversation"). Spawning is decided by the tools the parent grants. Check the tool list first. If spawning is unavailable, do the roles **sequentially yourself in wave order**, reading each owner's `knowledge/<agent>/` notes and keeping their file boundaries, and say so in the status report. Source: https://code.claude.com/docs/en/sub-agents (nesting, tool access), plus a direct check of this session's tools.
