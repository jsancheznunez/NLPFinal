---
name: python-testing
description: "Write and run pytest suites for the analyzer: fixtures, parametrized golden cases, schema validation and determinism checks. Use when adding tests or verifying Python work."
user-invocable: false
metadata:
  skill-id: S20
  shared-by: "data-engineer, nltk-expert, spacy-expert, metrics-engineer, build-pipeline-engineer, qa-engineer"
---

# Python testing (pytest) (S20)

Shared by: `data-engineer`, `nltk-expert`, `spacy-expert`, `metrics-engineer`, `build-pipeline-engineer`, `qa-engineer`. Matrix: `docs/expert-roster.md` §3.

- Session-scoped fixtures for expensive objects: `nlp` (spaCy) and `sia` (VADER), in `tests/conftest.py`.
- Golden cases with `@pytest.mark.parametrize`: VADER labels, aspect triples, stopword behavior and metric formulas.
- Fixtures data: `tests/fixtures/` (30 Subscription_Boxes reviews). Never use the network in tests.
- Pipeline test: run the build on the fixtures into `tmp_path`, check every expected file exists and validates against `schemas/`, and that a second run is byte-identical.
- Run with `pytest -q`. A task isn't done until its tests pass and the output is quoted in the summary.
Details: `knowledge/qa-engineer/pytest.md`, `knowledge/qa-engineer/json-schema-validation.md`.
