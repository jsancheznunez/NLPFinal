# Functions (not used) and environment variables

Sources:
- https://docs.netlify.com/build/functions/overview.md
- https://docs.netlify.com/build/environment-variables/overview.md
- https://docs.netlify.com/build/configure-builds/environment-variables.md

## Functions: why this project has none
- Netlify Functions are written in **TypeScript, JavaScript or Go**. Python isn't supported (see docs/04 for the full limits: 60 s synchronous, 15 min background, 1024 MB default memory, 6 MB buffered payload).
- The locked architecture runs Python only at build time and NLTK in Pyodide, so `netlify/functions/` stays empty. Any proposal for a function goes to the solution-architect and orchestrator.

## Environment variables
- Variables have a key, a **scope** and per-deploy-context values. "By default, environment variables apply to all scopes." Available scopes:
  - **Builds**: "use environment variables with this scope during the build step"
  - **Functions**: Functions, Edge Functions, etc.
  - **Runtime**: forms and signed proxy redirects
- Variables set in `netlify.toml` `[build.environment]` are available to the **build**. That's what we need for `PYTHON_VERSION` and `NLTK_DATA`.
- Read-only build variables (build environment variables page):
  - `CONTEXT`: "`production`, `deploy-preview`, `branch-deploy`, or `dev`"
  - `COMMIT_REF`: the SHA being built
  - `CACHED_COMMIT_REF`: the previous built SHA, the same as `COMMIT_REF` when building without cache
  - `DEPLOY_PRIME_URL`: the primary URL for this deploy or group
- `build_analysis.py` can stamp `COMMIT_REF` and `CONTEXT` into `site/data/summary.json` for traceability.
