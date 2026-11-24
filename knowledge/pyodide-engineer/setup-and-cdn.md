# Pyodide setup, CDN and deployment

Sources:
- https://pyodide.org/en/stable/usage/quickstart.html
- https://pyodide.org/en/stable/usage/downloading-and-deploying.html
- https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide-lock.json (checked Nov 2026)

## Pinned version for this project
- **Pyodide 314.0.8**. Its lockfile `info` reads `{'python': '3.14.2', 'platform': 'emscripten_5_0_3', 'arch': 'wasm32', 'abi_version': '2026_0'}`.
  - The browser runs **Python 3.14.2**, while the Netlify build runs Python 3.12. Shared code (`nltk_layer.py`) must work on both versions, so avoid syntax or stdlib features that only one of them has.
  - The lockfile lists `nltk 3.9.4`, which depends on `regex` (`regex-2026.3.32` wasm wheel). `nltk-3.9.4-py3-none-any.whl` is a pure-Python wheel.
- CDN URLs, which the docs list as "Recommended, cached by the browser":
  - Classic script: `https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.js` (checked: HTTP 200)
  - ES module: `https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.mjs`. Prefer this one. The docs say `pyodide.js` "Exports loadPyodide on globalThis. Legacy support... Prefer pyodide.mjs."
  - indexURL: `https://cdn.jsdelivr.net/pyodide/v314.0.8/full/`
  - **Never** use `.../pyodide/dev/full/`. It is "Re-deployed for each commit on main, no browser caching, should only be used for testing".
- The version string follows PEP 440 (`pyodide.version`).

## Minimal usage (docs)
```js
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.mjs";
const pyodide = await loadPyodide();
pyodide.runPython(`import sys; sys.version`);     // returns the last expression, converted to JS
```
- "After importing Pyodide, only packages from the standard library are available."
- `pyodide.runPython(code)` is synchronous. `pyodide.runPythonAsync(code, {globals})` supports top-level `await` and returns a Promise.

## Deploying (self-host vs. CDN)
- "Any service that hosts static files and that correctly sets the WASM MIME type and CORS headers will work." Netlify qualifies, but self-hosting means committing or serving the distribution, which is large ("200+ megabytes" for the full build, or the `pyodide-core-314.0.8.tar.bz2` minimal set).
- **Project decision: load Pyodide from the jsDelivr CDN** and serve only our own files (`nltk_layer.py`, `nltk_data/*.zip`) from Netlify.
- Core runtime files: `pyodide.mjs` (loader), `pyodide.asm.mjs` + `pyodide.asm.wasm` (the runtime), `python_stdlib.zip`, and `pyodide-lock.json` ("Necessary in all cases").
