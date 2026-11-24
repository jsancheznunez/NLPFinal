---
name: browser-perf-testing
description: "Keep the static site and Pyodide playground fast, and test them in a real browser with Playwright. Use for page weight, Web Worker, cold-load or end-to-end test work."
user-invocable: false
metadata:
  skill-id: S24
  shared-by: "frontend-engineer, pyodide-engineer, netlify-engineer, qa-engineer"
---

# Browser performance & testing (S24)

Shared by: `frontend-engineer`, `pyodide-engineer`, `netlify-engineer`, `qa-engineer`. Matrix: `docs/expert-roster.md` §3.

- Pyodide runs in a **module** Web Worker (`new Worker(url, {type: "module"})`). Show loading progress. A cold load downloads several MB from jsDelivr.
- Budgets: `site/` under 10 MB in total, `site/data` under 5 MB, dashboard JSON on first load under 500 KB.
- Cache: long `Cache-Control` for `/nltk_data/*`, short for `/data/*` (netlify.toml).
- Playwright (pytest plugin): `pytest --base-url <deploy-preview-url> --tracing off`. Use role-based locators and `expect(...).to_have_text(..., timeout=60_000)` for the playground's first run. Assert there are no console errors.
- In the cloud sandbox, Chromium and Playwright are pre-installed. Don't run `playwright install`.
Details: `knowledge/qa-engineer/playwright.md`, `knowledge/pyodide-engineer/web-worker.md`.
