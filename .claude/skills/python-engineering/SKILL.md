---
name: python-engineering
description: "Write clean, typed, testable Python modules for the analyzer that run on Python 3.12 (build) and, for shared code, Python 3.14 (Pyodide). Use for any Python module, script or package layout work."
user-invocable: false
metadata:
  skill-id: S07
  shared-by: "solution-architect, data-engineer, nltk-expert, spacy-expert, metrics-engineer, build-pipeline-engineer"
---

# Python 3.12 engineering (S07)

Shared by: `solution-architect`, `data-engineer`, `nltk-expert`, `spacy-expert`, `metrics-engineer`, `build-pipeline-engineer`. Matrix: `docs/expert-roster.md` §3.

- Layout: `analyzer/` (library: `nltk_layer.py`, `spacy_layer.py`, `metrics.py`), `scripts/` (entry points), `tests/`.
- Pure functions with type hints. Keep I/O at the edges (scripts) and computation in `analyzer/`.
- Shared code (`nltk_layer.py`) must run on **both 3.12 and 3.14**. No third-party imports beyond `nltk`, no file-system assumptions, no `nltk.download()`.
- Module-level singletons for expensive objects (spaCy `nlp`, VADER analyzer), created lazily.
- Deterministic output: sort before writing, stable tie-breakers, round floats to 4 decimals.
- Log with `logging`, not `print`, in library code. Exit with a non-zero code on validation failure in scripts.
- Dependencies: see `knowledge/build-pipeline-engineer/requirements-and-pins.md`.
