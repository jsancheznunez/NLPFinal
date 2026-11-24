# Knowledge: pyodide-engineer

Reference notes from the official Pyodide docs (pyodide.org/en/stable, version **314.0.8**), the Pyodide lockfile, and MDN. Read this index first.

| File | Covers | Main sources |
|---|---|---|
| [setup-and-cdn.md](setup-and-cdn.md) | CDN URL, `loadPyodide`, running Python, versions in the lockfile, deploying static files | pyodide.org/en/stable/usage/quickstart.html, …/downloading-and-deploying.html, pyodide-lock.json |
| [loading-packages.md](loading-packages.md) | `loadPackage` vs `micropip`, NLTK availability, why spaCy fails | …/loading-packages.html, …/packages-in-pyodide.html |
| [web-worker.md](web-worker.md) | The documented module-worker pattern, plus MDN worker basics | …/webworker.html, developer.mozilla.org Using_web_workers |
| [filesystem-and-nltk-data.md](filesystem-and-nltk-data.md) | `pyodide.FS`, `unpackArchive`, mounting NLTK data | …/file-system.html, …/api/js-api.html |
| [type-conversions-and-limits.md](type-conversions-and-limits.md) | Python↔JS conversion, `toJs`, proxies, stdlib limits | …/type-conversions.html, …/wasm-constraints.html |

Project context: [docs/04-netlify-deployment.md](../../docs/04-netlify-deployment.md). Coordinate with `nltk-expert`: the browser runs **the same `nltk_layer.py`** as the build.
