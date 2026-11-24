# Project plan (from docs/expert-roster.md)

## Dependency order
1. **Design:** solution-architect freezes `schemas/*.schema.json` and the repo layout. meta-agent checks the agent prompts.
2. **Data:** data-engineer commits `data/sample/` and `tests/fixtures/`.
3. **NLP layers** (can run in parallel once the data exists): spacy-expert builds `analyzer/spacy_layer.py`, and nltk-expert builds `analyzer/nltk_layer.py`. The NLTK layer consumes spaCy lemmas through a plain list-of-strings interface, so the two can be built at the same time against fixtures.
4. **Metrics:** metrics-engineer builds `analyzer/metrics.py`.
5. **Pipeline:** build-pipeline-engineer builds `scripts/build_analysis.py` and `requirements.txt`, producing `site/data/*.json`.
6. **Web** (in parallel): frontend-engineer builds the pages, and pyodide-engineer builds the playground.
7. **Deploy:** netlify-engineer writes `netlify.toml` and opens the first Deploy Preview.
8. **Test:** qa-engineer runs on every PR.
9. **Deliver:** eval-report-writer writes `docs/evaluation.md`, the README and the report.

## Milestone gates
| # | Gate | Evidence |
|---|---|---|
| M1 | Contract frozen | schemas merged; `check_schema` tests pass |
| M2 | Pipeline green locally | `python scripts/build_analysis.py` on the sample passes schema validation in less than half the time budget |
| M3 | First Deploy Preview | dashboard shows real data; Playwright passes |
| M4 | Playground live | Pyodide + NLTK scores match the build within 1e-4 |
| M5 | Production + report | evaluation numbers in; limitations written; single production deploy |

## Definition of done (every task)
The code follows the owning agent's knowledge notes, the tests pass, the JSON validates, no rule in CLAUDE.md is broken, and there's a short summary of what changed and how it was verified.
