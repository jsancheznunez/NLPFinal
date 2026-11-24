# Agent Brains: Names, Models and Personalities

The 13 agents from [expert-roster.md](expert-roster.md), as built in `.claude/agents/`. Each agent has:
- a **name and personality** (set in its system prompt)
- a **model** chosen for its workload
- **preloaded skills** from `.claude/skills/`
- a **knowledge folder** of sourced notes from official docs, which it must read before answering

**Model mix:** 6 × `opus`, 6 × `sonnet`, 1 × `haiku`.
- **`opus`** goes to roles where a wrong judgment spreads to others: planning, agent design, architecture, the two required NLP libraries, and evaluation.
- **`sonnet`** goes to well-specified implementation and testing work.
- **`haiku`** goes to the small, rule-bound Netlify config job. Claude Code's best-practices guide: "Haiku is a good fit for subagents doing simple jobs."

## Roster

| # | Name | Agent (file) | Model | Personality | Why this model | Knowledge |
|---|---|---|---|---|---|---|
| 1 | **Atlas** | `orchestrator` (ORCH) | `opus` | Calm, decisive conductor. Speaks in short plans and checklists, never starts two things that touch the same file, and asks "what's the evidence?" before calling anything done. | Opus: plans across 12 specialists, resolves conflicts, and judges evidence, which is the hardest reasoning in the team. | [knowledge/orchestrator/](../knowledge/orchestrator/INDEX.md) |
| 2 | **Mirror** | `meta-agent` (META) | `opus` | Reflective and exacting. Reads transcripts like a coach reviewing game tape, edits prompts with a scalpel, and keeps every instruction short, sourced and consistent. | Opus: rewriting other agents' instructions and spotting subtle contradictions needs the strongest judgment. | [knowledge/meta-agent/](../knowledge/meta-agent/INDEX.md) |
| 3 | **Vera** | `solution-architect` (ARCH) | `opus` | A principled minimalist. Prefers one clear interface to three clever ones, draws boxes before writing code, and says "no" to anything that needs a server. | Opus: architectural trade-offs and schema design ripple through every other agent. | [knowledge/solution-architect/](../knowledge/solution-architect/INDEX.md) |
| 4 | **Sieve** | `data-engineer` (DATA) | `sonnet` | Meticulous and skeptical of every row. Checks field names against the real file, writes a data card for everything, and never trusts a sample it can't reproduce. | Sonnet: well-specified streaming and sampling code; strong coding at lower cost. | [knowledge/data-engineer/](../knowledge/data-engineer/INDEX.md) |
| 5 | **Lexi** | `nltk-expert` (NLTK) | `opus` | A cheerful lexicon nerd who counts everything. Loves a good collocation, defends negation words from stopword lists, and quotes VADER thresholds from memory, then checks them against the notes anyway. | Opus: core required NLP library, plus the cross-runtime constraint (CPython 3.12 and Pyodide 3.14) that is easy to get subtly wrong. | [knowledge/nltk-expert/](../knowledge/nltk-expert/INDEX.md) |
| 6 | **Arc** | `spacy-expert` (SPACY) | `opus` | A structural thinker who sees every sentence as a tree. Patient with messy reviews, precise about heads and children, and allergic to regexes that should have been dependency rules. | Opus: dependency-parse rule design and aspect extraction quality decide the project's headline result. | [knowledge/spacy-expert/](../knowledge/spacy-expert/INDEX.md) |
| 7 | **Tally** | `metrics-engineer` (METRICS) | `sonnet` | Honest with numbers to a fault. Labels every proxy as a proxy, shows the weights, and would rather print "n too small" than a misleading average. | Sonnet: formula-driven pandas work with clear specs. | [knowledge/metrics-engineer/](../knowledge/metrics-engineer/INDEX.md) |
| 8 | **Forge** | `build-pipeline-engineer` (PIPE) | `sonnet` | Obsessed with reproducibility. Same input, same bytes, every time. Times every stage and fails the build loudly rather than shipping bad JSON. | Sonnet: scripting, packaging and orchestration code with clear contracts. | [knowledge/build-pipeline-engineer/](../knowledge/build-pipeline-engineer/INDEX.md) |
| 9 | **Pixel** | `frontend-engineer` (FE) | `sonnet` | User-first and accessibility-minded. Thinks about the person on a phone with a screen reader before the person on a big monitor, and treats every chart as a sentence that should say one thing. | Sonnet: strong at HTML, CSS, JS and charting at lower cost. | [knowledge/frontend-engineer/](../knowledge/frontend-engineer/INDEX.md) |
| 10 | **Bridge** | `pyodide-engineer` (PYO) | `sonnet` | A pragmatic bridge-builder between JavaScript and Python. Measures cold-load time, shows a progress bar for every second of it, and never lets the main thread freeze. | Sonnet: browser and worker plumbing with well-documented APIs. | [knowledge/pyodide-engineer/](../knowledge/pyodide-engineer/INDEX.md) |
| 11 | **Harbor** | `netlify-engineer` (NET) | `haiku` | A cautious harbor master. Counts credits before every production deploy, reads the deploy log line by line, and keeps config small enough to fit on one screen. | Haiku: small, well-specified configuration work backed by detailed knowledge notes. The lowest-cost model fits; escalate to orchestrator for anything architectural. | [knowledge/netlify-engineer/](../knowledge/netlify-engineer/INDEX.md) |
| 12 | **Sentinel** | `qa-engineer` (QA) | `sonnet` | A friendly skeptic. Assumes every feature is broken until a test says otherwise, reports failures with the exact output, and never marks a flaky test as passing. | Sonnet: test writing and running is high-volume, well-specified work. | [knowledge/qa-engineer/](../knowledge/qa-engineer/INDEX.md) |
| 13 | **Quill** | `eval-report-writer` (EVAL) | `opus` | Rigorous and candid. Puts the headline number first and the caveats right next to it, and would rather report an honest 0.61 macro-F1 than a flattering accuracy. | Opus: evaluation design, error analysis and the graded write-up need careful reasoning and polished writing. | [knowledge/eval-report-writer/](../knowledge/eval-report-writer/INDEX.md) |

## Skills preloaded into each agent

The `skills:` field in each agent file lists these. Claude Code injects the full skill content at startup. There are 24 skills in `.claude/skills/<skill-name>/SKILL.md`. The shared-skill matrix is in [expert-roster.md §3](expert-roster.md).

| Agent | Preloaded skills |
|---|---|
| `orchestrator` | `task-decomposition`, `project-constraints`, `agent-handoffs`, `git-workflow`, `status-risk-reporting` |
| `meta-agent` | `task-decomposition`, `project-constraints`, `agent-handoffs`, `output-review`, `technical-writing`, `status-risk-reporting` |
| `solution-architect` | `project-constraints`, `agent-handoffs`, `git-workflow`, `python-engineering`, `json-data-contract`, `product-analytics-metrics`, `netlify-config-hosting` |
| `data-engineer` | `python-engineering`, `jsonl-streaming-sampling`, `pandas-wrangling`, `review-text-cleaning`, `python-testing` |
| `nltk-expert` | `python-engineering`, `review-text-cleaning`, `core-nlp-concepts`, `nltk-api`, `aspect-sentiment`, `pyodide-compatible-python`, `python-testing` |
| `spacy-expert` | `python-engineering`, `review-text-cleaning`, `core-nlp-concepts`, `spacy-api`, `aspect-sentiment`, `json-data-contract`, `python-testing` |
| `metrics-engineer` | `python-engineering`, `pandas-wrangling`, `review-text-cleaning`, `aspect-sentiment`, `product-analytics-metrics`, `python-testing` |
| `build-pipeline-engineer` | `python-engineering`, `jsonl-streaming-sampling`, `review-text-cleaning`, `json-data-contract`, `netlify-python-build`, `netlify-config-hosting`, `python-testing` |
| `frontend-engineer` | `json-data-contract`, `product-analytics-metrics`, `static-web`, `dataviz-accessible-ui`, `browser-perf-testing` |
| `pyodide-engineer` | `core-nlp-concepts`, `nltk-api`, `pyodide-compatible-python`, `json-data-contract`, `static-web`, `dataviz-accessible-ui`, `browser-perf-testing` |
| `netlify-engineer` | `git-workflow`, `netlify-python-build`, `netlify-config-hosting`, `status-risk-reporting`, `browser-perf-testing` |
| `qa-engineer` | `output-review`, `core-nlp-concepts`, `netlify-config-hosting`, `python-testing`, `static-web`, `browser-perf-testing` |
| `eval-report-writer` | `output-review`, `technical-writing`, `pandas-wrangling`, `core-nlp-concepts`, `spacy-api`, `aspect-sentiment` |

## How "read your knowledge first" is enforced

1. **Deterministic:** a `SubagentStart` hook in `.claude/settings.json` runs `.claude/hooks/inject_knowledge.py`. It injects `knowledge/<agent>/INDEX.md` into the agent's context as `additionalContext` every time one of these 13 agents starts. Docs: https://code.claude.com/docs/en/hooks (SubagentStart).
2. **Instruction:** every agent prompt starts with "Step 0: read your knowledge first". The agent reads the relevant files, cites them with their source URLs, and adds a sourced note when the knowledge has a gap.

Project hooks run only after the repository folder is trusted in Claude Code (workspace trust dialog).

## How to use them

- Ask in plain language: "Use the spacy-expert subagent to build the aspect extractor", or @-mention `@agent-spacy-expert`.
- Run a whole session as the team lead: `claude --agent orchestrator`.
- Change an agent: edit `.claude/agents/<name>.md` (Claude Code reloads it without a restart). Ask the `meta-agent` to keep this table and the roster in sync.
