---
name: pyodide-compatible-python
description: "Rules for Python that must run both in the Netlify build (CPython 3.12) and in the browser (Pyodide 314.0.8, Python 3.14.2). Use when editing analyzer/nltk_layer.py or anything loaded by the playground."
user-invocable: false
metadata:
  skill-id: S15
  shared-by: "nltk-expert, pyodide-engineer"
---

# Writing Pyodide-compatible Python (S15)

Shared by: `nltk-expert`, `pyodide-engineer`. Matrix: `docs/expert-roster.md` §3.

- Imports allowed in shared code: the standard library, `nltk` (3.9.4) and `regex`. **No spaCy, pandas or numpy** in `nltk_layer.py`.
- No network or downloads (`ssl` is a stub in Pyodide). No `nltk.download()`, no `requests`.
- No hard-coded paths. Data paths come from `nltk.data.path`, which the caller sets (`/nltk_data` in Pyodide, `$NLTK_DATA` in the build).
- No threads or multiprocessing, no `tkinter`, no `.plot()`.
- Return plain `dict`/`list`/`float`/`str` (JSON-serializable), so JS can use `toJs({dict_converter: Object.fromEntries})` or `json.dumps`.
- Keep it fast: build the analyzer and stopword set once at module level, lazily.
- Test it: a pytest case runs the module under the build Python, and a Playwright case runs it in Pyodide. Scores must match within 1e-4.
Details: `knowledge/pyodide-engineer/`.
