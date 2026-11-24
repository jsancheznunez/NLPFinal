# Type conversions and Pyodide limits

Sources:
- https://pyodide.org/en/stable/usage/type-conversions.html
- https://pyodide.org/en/stable/usage/wasm-constraints.html
- https://pyodide.org/en/stable/usage/api/js-api.html

## Python → JS
- `runPython`/`runPythonAsync` return the last expression. Immutable types (str, int, float, bool, None) convert automatically. Containers come back as a **`PyProxy`**.
- `proxy.toJs()` converts deeply. By default a Python `dict` becomes a JS **`Map`**. "If you need to convert `dict` instead to `Object`, you can pass `Object.fromEntries()` as the `dict_converter` argument: `proxy.toJs({dict_converter: Object.fromEntries})`." **Always do this** for results that go to `postMessage` or JSON.
- Proxies hold Python memory. Call `proxy.destroy()` when you're done with one ("Memory Leaks and toJs" section).
- A simpler alternative: return `json.dumps(result)` from Python and `JSON.parse` it in JS. No proxies are involved.

## JS → Python
- `pyodide.globals.set("name", value)` and `pyodide.globals.get("name")`. "An alias to the global Python namespace."
- `pyodide.toPy(obj, {depth})` converts a JS object to Python.

## Standard-library limits (wasm-constraints)
- "Most of the Python standard library is functional." Limited modules: `ssl` ("replaced with a stub implementation that does not use OpenSSL"), `hashlib` (no OpenSSL algorithms), `zoneinfo` (needs `tzdata`), `decimal`, `pydoc`, `webbrowser`.
- Removed modules (docs list): `curses`, `dbm`, `ensurepip`, `fcntl`, `grp`, `idlelib`, `lib2to3`, `msvcrt`, `pwd`, `resource`, `syslog`, `termios`, `tkinter`, `turtle`, `venv`, `winreg`, `winsound`. NLTK features that open GUIs (`nltk.download()` with no args, `FreqDist.plot`) are therefore unavailable.
- Networking: "all network calls are done via the browser... constrained by browser policies relating to cross-origin requests." Fetch only same-origin files (our Netlify site) or CORS-enabled CDNs.

## Performance tips for the playground
- Load once and reuse the analyzer. Cap input text length (e.g. 5,000 characters) to keep responses quick.
- Show a progress UI. The first visit downloads the Pyodide runtime, stdlib, `nltk` and `regex` wheels, and our data zips. jsDelivr responses are cached by the browser afterwards.
