# Verified platform constraints (summary; details in the linked notes)

| Constraint | Value | Detail |
|---|---|---|
| Netlify build OS | Ubuntu 24.04 | netlify-engineer/build-image-and-python.md |
| Build Python | `PYTHON_VERSION=3.12` (any official version allowed) | same |
| Python dependency install | automatic `pip install` of `requirements.txt` in the base directory | same |
| Deployed files | **only the publish directory** (`site/`) | netlify-engineer/build-settings-and-netlify-toml.md |
| Netlify Functions | TS/JS/Go only. **Not used.** | netlify-engineer/functions-and-env-vars.md |
| Production deploy cost | 15 credits each; Deploy Previews 0; Free plan 300 credits/month | netlify-engineer/deploys-previews-and-credits.md |
| Pyodide | 314.0.8 from jsDelivr; runs **Python 3.14.2** in the browser | pyodide-engineer/setup-and-cdn.md |
| NLTK in browser | `nltk 3.9.4` via `loadPackage("nltk")` → **pin the build to `nltk==3.9.4`** | pyodide-engineer/loading-packages.md |
| spaCy in browser | **impossible** (no wasm builds of thinc/blis/cymem/preshed…) | same |
| Worker | must be a **module** worker | pyodide-engineer/web-worker.md |
| NLTK data in browser | served as static zips and written into Pyodide's in-memory FS; never `nltk.download()` | pyodide-engineer/filesystem-and-nltk-data.md |
| spaCy model | `en_core_web_sm` 3.8.0, 12 MB, requires spaCy `>=3.8.0,<3.9.0`, installed via a direct wheel URL in requirements.txt | spacy-expert/en-core-web-sm.md |
| Dataset timestamps | Unix **milliseconds**; field names `timestamp` and `helpful_vote` (verified) | data-engineer/amazon-reviews-2023.md |
| JSON for the browser | `allow_nan=False` (browsers reject NaN) | data-engineer/streaming-and-sampling.md |
| Shared code | `nltk_layer.py` must run on both Python 3.12 and 3.14 | — |
