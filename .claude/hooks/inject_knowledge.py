#!/usr/bin/env python3
"""SubagentStart hook: inject knowledge/<agent>/INDEX.md into a project subagent.

Claude Code passes the event as JSON on stdin; `agent_type` is the subagent's
frontmatter `name`. If knowledge/<agent_type>/INDEX.md exists, we return it as
`additionalContext` so the agent always starts with its reference index.
Docs: https://code.claude.com/docs/en/hooks.md (SubagentStart)
"""
import json
import os
import pathlib
import sys

try:
    event = json.load(sys.stdin)
except Exception:
    sys.exit(0)

agent = str(event.get("agent_type", ""))
root = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or ".")
index = root / "knowledge" / agent / "INDEX.md"
if not agent or "/" in agent or ".." in agent or not index.is_file():
    sys.exit(0)

files = sorted(p.name for p in index.parent.glob("*.md") if p.name != "INDEX.md")
context = (
    f"KNOWLEDGE FIRST: you are `{agent}`. Before answering or editing, Read the files in "
    f"knowledge/{agent}/ that relate to this task ({', '.join(files)}), and cite them with their "
    f"source URLs. Your index follows.\n\n" + index.read_text(encoding="utf-8")
)
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": context}}))
