---
name: netlify-config-hosting
description: "Configure netlify.toml, publish directory, headers, ignore rules, Deploy Previews and credit-aware deploys for the static site. Use for any netlify.toml, header, deploy or hosting question."
user-invocable: false
metadata:
  skill-id: S19
  shared-by: "solution-architect, build-pipeline-engineer, netlify-engineer, qa-engineer"
---

# Netlify config & static hosting (S19)

Shared by: `solution-architect`, `build-pipeline-engineer`, `netlify-engineer`, `qa-engineer`. Matrix: `docs/expert-roster.md` §3.

- `netlify.toml`: `[build] command = "python scripts/build_analysis.py"`, `publish = "site"`; `[build.environment] PYTHON_VERSION = "3.12"`; add `"$schema" = "https://open-api.netlify.com/netlify.schema.json"`.
- Headers through `[[headers]]` (global for all contexts): short cache for `/data/*`, a long cache for `/nltk_data/*`, `X-Content-Type-Options: nosniff`. **No COOP/COEP headers** (they'd break the Pyodide CDN script).
- Deploy Previews are built for every PR (`deploy-preview-<n>--<site>.netlify.app`) and cost 0 credits. Production deploys cost 15 credits each.
- Optional `ignore` command to skip builds when only `docs/`, `knowledge/` or `.claude/` changed (exit 0 = skip).
- Build variables available: `CONTEXT`, `COMMIT_REF`, `CACHED_COMMIT_REF`, `DEPLOY_PRIME_URL`.
Details: `knowledge/netlify-engineer/`.
