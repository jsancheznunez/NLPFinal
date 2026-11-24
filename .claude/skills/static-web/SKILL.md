---
name: static-web
description: "Build the static dashboard and playground pages that read precomputed JSON, with no backend. Use for any file under site/."
user-invocable: false
metadata:
  skill-id: S22
  shared-by: "frontend-engineer, pyodide-engineer, qa-engineer"
---

# Static HTML/CSS/JS (no backend) (S22)

Shared by: `frontend-engineer`, `pyodide-engineer`, `qa-engineer`. Matrix: `docs/expert-roster.md` §3.

- Plain HTML, CSS and ES modules. No build step is needed. Optional libraries come from jsDelivr with **exact pinned versions** (e.g. `chart.js@4.5.1`).
- Data: `fetch("data/…json")` with a `response.ok` check and a visible error state (`knowledge/frontend-engineer/static-data-loading.md`). Use relative paths so Deploy Previews work.
- Pages: `index.html` (dashboard), `product.html?asin=…`, `trends.html`, `how-it-works.html` (displaCy), `playground.html` (Pyodide).
- Shared `assets/app.css` and `assets/util.js`. No inline secrets (there are none).
- Local preview: `python -m http.server -d site 8080`.
