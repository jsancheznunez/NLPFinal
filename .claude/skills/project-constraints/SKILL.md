---
name: project-constraints
description: "The non-negotiable constraints of the Ecommerce Product Performance Analyzer: Netlify only, spaCy at build time, NLTK at build time and in Pyodide. Use whenever a design, file or dependency choice is being made."
user-invocable: false
metadata:
  skill-id: S02
  shared-by: "orchestrator, meta-agent, solution-architect"
---

# Project constraints (locked Netlify-only architecture) (S02)

Shared by: `orchestrator`, `meta-agent`, `solution-architect`. Matrix: `docs/expert-roster.md` §3.

Locked decisions (docs/04-netlify-deployment.md, docs/expert-roster.md):
1. **Everything runs on Netlify.** No outside servers, no Python Netlify Functions (Functions are TS/JS/Go only), no databases, no runtime APIs.
2. **spaCy runs only in the Netlify Python build** (Python 3.12). It cannot run in Pyodide.
3. **NLTK runs in the build and in the browser** (Pyodide 314.0.8, which ships Python 3.14.2 and nltk 3.9.4) from **the same `analyzer/nltk_layer.py`**. Pin `nltk==3.9.4`.
4. Only `site/` is deployed. Generated JSON goes in `site/data/`, the browser copy of `nltk_layer.py` in `site/py/`, and NLTK zips in `site/nltk_data/`.
5. Never download the full dataset during the Netlify build. Use the committed `data/sample/` only.
6. Sales numbers are **proxies**. Any synthetic sales data is labeled **simulated**.
7. Every JSON file validates against `schemas/*.schema.json` and is written with `allow_nan=False`.
Refer anything that breaks a rule to solution-architect and orchestrator. Never work around a rule quietly.
Verified details: `knowledge/solution-architect/platform-constraints.md`.
