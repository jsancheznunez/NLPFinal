---
name: technical-writing
description: "Write clear project docs, the final report, READMEs, agent prompts and skill files. Use when producing any prose deliverable."
user-invocable: false
metadata:
  skill-id: S06
  shared-by: "meta-agent, eval-report-writer"
---

# Technical writing (docs, reports, skill files) (S06)

Shared by: `meta-agent`, `eval-report-writer`. Matrix: `docs/expert-roster.md` §3.

- Lead with the answer or result, then the supporting detail. Short sentences, plain words, define each term once.
- Every factual claim about a library or platform cites its source URL, taken from the relevant `knowledge/` note.
- Use tables for comparisons and metrics, and code blocks for commands and config.
- The report must include: problem, data (with citation and license status), method (NLTK vs spaCy roles), architecture (Netlify constraints), evaluation numbers, limitations, and how to reproduce.
- Skill and agent files: concise, imperative, under 500 lines (`knowledge/meta-agent/skill-files.md`).
