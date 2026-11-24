---
name: json-data-contract
description: "Design, write and honor the JSON Schemas (2020-12) that connect the Python build output to the static site and Pyodide page. Use when adding or changing any file in site/data/ or schemas/."
user-invocable: false
metadata:
  skill-id: S16
  shared-by: "solution-architect, spacy-expert, build-pipeline-engineer, frontend-engineer, pyodide-engineer"
---

# JSON data contract / JSON Schema design (S16)

Shared by: `solution-architect`, `spacy-expert`, `build-pipeline-engineer`, `frontend-engineer`, `pyodide-engineer`. Matrix: `docs/expert-roster.md` §3.

- Schemas live in `schemas/<file>.schema.json` and use `"$schema": "https://json-schema.org/draft/2020-12/schema"`, `$id`, `title`, `type`, `properties`, `required`, and `additionalProperties: false`.
- Files: `summary.json`, `products.json`, `product/<parent_asin>.json`, `aspects.json`, `trends.json`, `build_info.json` (outline in `knowledge/solution-architect/json-schema-contract.md`).
- Rules: floats rounded to 4 decimals; ISO dates (`YYYY-MM` for months); `null`, never NaN; deterministic sort order; each metric carries `metric_kind` (`"proxy"` where relevant).
- Change process: solution-architect updates the schema first, then the producer (pipeline) and consumers (frontend, pyodide) update in the same PR, and QA's schema tests must pass.
- Validate with `jsonschema.Draft202012Validator` and fail the build on any error.
