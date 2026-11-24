---
name: output-review
description: "Review another agent's code, data or docs for correctness and consistency with the project docs and knowledge notes. Use before merging, after an agent finishes a task, or when outputs disagree."
user-invocable: false
metadata:
  skill-id: S05
  shared-by: "meta-agent, qa-engineer, eval-report-writer"
---

# Reviewing output for correctness & consistency (S05)

Shared by: `meta-agent`, `qa-engineer`, `eval-report-writer`. Matrix: `docs/expert-roster.md` §3.

Checklist:
1. **Matches the docs?** Compare against docs/01–04, `project-constraints`, and the owner's `knowledge/<agent>/` notes. Flag any claim that has no source.
2. **Interfaces:** JSON validates against `schemas/`, and function signatures match what downstream agents expect.
3. **Evidence:** a test, a command output or a file diff proves each claim of "done". "Looks right" isn't evidence.
4. **Honesty:** proxies are labeled, limitations are stated, nothing is silently simulated.
5. **Version pins** agree everywhere: `nltk==3.9.4` (= Pyodide), spaCy 3.8.x with `en_core_web_sm` 3.8.0, Pyodide 314.0.8.
Report findings as: file:line, what's wrong, why it matters, and the fix. Rank them by severity.
