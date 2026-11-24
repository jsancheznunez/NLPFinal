# CLAUDE.md: Ecommerce Product Performance Analyzer

NLP final project. The app analyzes online products from reviews and product data. It finds best-sellers, measures sentiment and performance, and surfaces trends and opportunities. It **must use both NLTK and spaCy** and **must deploy on Netlify**.

## Locked architecture (never work around it)
- **Netlify only.** No outside servers, databases or runtime APIs. No Python Netlify Functions (Functions are TS/JS/Go only).
- **Build time:** Netlify runs Python 3.12 and `python scripts/build_analysis.py`. That runs **spaCy + NLTK** over the committed `data/sample/` and writes static JSON to `site/data/`. Only `site/` is deployed.
- **Runtime:** a static dashboard reads that JSON. The "Analyze your own review" page runs **NLTK live in the browser with Pyodide 314.0.8** (Python 3.14, nltk 3.9.4) in a module Web Worker.
- **spaCy never runs in the browser.** Pyodide can't load it.
- **Shared code:** `analyzer/nltk_layer.py` runs unchanged in the build and in Pyodide. Pin `nltk==3.9.4`.
- **Data:** a sample of Amazon Reviews 2023 (McAuley Lab). Sales figures are **proxies**, and any synthetic sales data is labeled **simulated**. Cite the dataset. No license is declared, so use it for academic, non-commercial work only.

## The team (`.claude/agents/`)
| Agent | Name | Model | Job |
|---|---|---|---|
| `orchestrator` | Atlas | opus | Plans, delegates, enforces gates, merges |
| `meta-agent` | Mirror | opus | Maintains agents, skills, knowledge and the roster |
| `solution-architect` | Vera | opus | Architecture, repo layout, JSON schemas |
| `data-engineer` | Sieve | sonnet | Samples the dataset into `data/sample/` |
| `nltk-expert` | Lexi | opus | `analyzer/nltk_layer.py` (VADER, FreqDist, collocations) |
| `spacy-expert` | Arc | opus | `analyzer/spacy_layer.py` (NER, noun chunks, lemmas, dependency aspects, displaCy) |
| `metrics-engineer` | Tally | sonnet | `analyzer/metrics.py` (score, trends, opportunities) |
| `build-pipeline-engineer` | Forge | sonnet | `scripts/build_analysis.py`, `requirements.txt` |
| `frontend-engineer` | Pixel | sonnet | Static pages and charts in `site/` |
| `pyodide-engineer` | Bridge | sonnet | In-browser NLTK playground |
| `netlify-engineer` | Harbor | haiku | `netlify.toml`, headers, deploys |
| `qa-engineer` | Sentinel | sonnet | pytest, schema checks, Playwright |
| `eval-report-writer` | Quill | opus | Evaluation, limitations, final report |

Start a session as the lead with `claude --agent orchestrator`, or ask for an agent by name ("Use the spacy-expert subagent to…"). Personalities and model choices: `docs/agent-brains.md`. Roles and the skill matrix: `docs/expert-roster.md`.

## Where things live
- `docs/`: research and decisions (index: `docs/README.md`).
- `.claude/agents/`: the 13 subagents. Each preloads its skills.
- `.claude/skills/<skill>/SKILL.md`: the 24 shared skills (S01–S24).
- `knowledge/<agent>/`: sourced notes from official docs, one folder per agent. **Agents read their folder before answering.** A `SubagentStart` hook (`.claude/settings.json` → `.claude/hooks/inject_knowledge.py`) injects `INDEX.md`.

## Working rules
- One task per branch and PR. Every PR gets a free Netlify Deploy Preview. **Merge to `main` only at milestones**, because each production deploy costs 15 credits (Free plan: 300/month).
- Done means verified: tests pass, JSON validates against `schemas/`, and the command output is quoted in the summary.
- Every new fact about a library or platform goes into the right `knowledge/` note with its source URL.
- Keep this file under 200 lines. Put details in `docs/` or `knowledge/`, not here.
