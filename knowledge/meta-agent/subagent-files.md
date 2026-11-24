# Subagent files

Source: https://code.claude.com/docs/en/sub-agents.md (Write subagent files, Frontmatter reference, Choose a model, Control subagent capabilities, Preload skills, Enable persistent memory, Define hooks). Also https://code.claude.com/docs/en/hooks.md (SubagentStart).

## Format
- Markdown with YAML frontmatter. "The body becomes the system prompt." Subagents get this prompt "plus basic environment details like the working directory, not the Claude Code system prompt."
- Project scope is `.claude/agents/`. Claude Code watches it: "the next delegation uses the updated definition, with no restart needed."
- **Only `name` and `description` are required.** Multi-word fields use camelCase and "must match the table exactly: Claude Code ignores a field it doesn't recognize without reporting an error."
- A file is **skipped** if it has no `name`, the opening `---` isn't the first line, the name starts with `-`, contains `:` or is over 256 characters, it has a `name` but no `description`, or the YAML doesn't parse. Check with `claude plugin validate .claude/agents`.

## Fields used in this repo
| Field | Use |
|---|---|
| `name` | kebab-case ID (`nltk-expert`). Hooks see it as `agent_type` |
| `description` | When to delegate. Add "Use proactively" to encourage automatic delegation. Combined descriptions should stay well under the 15,000-token warning |
| `tools` | Allowlist (comma-separated). Omit it to inherit everything. Don't list `Skill` to preload skills; use `skills` |
| `model` | `opus`, `sonnet`, `haiku`, `fable`, a full ID, or `inherit` |
| `skills` | "The full content of each listed skill is injected into the subagent's context at startup", up to 32 names. Skills with `disable-model-invocation: true` can't be preloaded |
| `color` | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink` or `cyan` |
| `effort` | `low`, `medium`, `high`, `xhigh` or `max` (optional) |
| `memory` | `user`, `project` or `local`. `project` uses `.claude/agent-memory/<name>/` (shareable through git). Not used yet |
Other fields: `disallowedTools`, `permissionMode`, `maxTurns`, `mcpServers`, `hooks`, `background`, `omitClaudeMd`, `isolation: worktree`, `initialPrompt`.

## Model choice order
1. The per-invocation `model` parameter
2. The frontmatter `model`
3. `CLAUDE_CODE_SUBAGENT_MODEL`
4. The parent's model

Best practices: "Haiku is a good fit for subagents doing simple jobs." "Set `model: haiku`... if its work is simple."

## Background tool set
Background subagents keep `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write`, `NotebookEdit`, `WebFetch`, `WebSearch`, `TodoWrite`, `Skill`, `ToolSearch`, `SendMessage` and MCP tools. Don't depend on other built-in tools in agent prompts.

## Knowledge injection hook (used here)
- `SubagentStart` "can't block subagent creation, but they can inject context into the subagent" by returning `{"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": "..."}}`. The input JSON includes `agent_type`, which equals the frontmatter `name`.
- Project frontmatter hooks need workspace trust. Settings-file hooks fire in subagents too.
