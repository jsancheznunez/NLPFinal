# Running Pyodide in a Web Worker

Sources:
- https://pyodide.org/en/stable/usage/webworker.html
- https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers

## Why use a worker (Pyodide docs)
- "A lot of Python programs do long-running synchronous computations. Running them in the main thread blocks the UI. Using a web worker is advantageous because the Python code runs in a separate thread."
- "a worker cannot directly manipulate the DOM." The worker only posts results back to the page.
- **"Pyodide requires a module-type worker because `pyodide.asm.mjs` is an ES module. Classic workers using `importScripts()` are not supported."** So create it with `new Worker("./pyodide-worker.mjs", { type: "module" })`.

## Pattern from the docs (adapted)
```js
// site/assets/pyodide-worker.mjs
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.mjs";
const ready = (async () => {
  const py = await loadPyodide();
  await py.loadPackage("nltk");
  // mount nltk_data + nltk_layer.py here (see filesystem-and-nltk-data.md)
  return py;
})();

self.onmessage = async (event) => {
  const py = await ready;
  const { id, text } = event.data;
  try {
    py.globals.set("review_text", text);
    const proxy = await py.runPythonAsync("import nltk_layer; nltk_layer.analyze(review_text)");
    const result = proxy.toJs({ dict_converter: Object.fromEntries });
    proxy.destroy();
    self.postMessage({ id, result });
  } catch (error) {
    self.postMessage({ id, error: error.message });
  }
};
```
- The docs' worker API tags each message with an `id`, posts it, and resolves a Promise when a reply with the same `id` arrives. Use that request/response pattern so overlapping requests don't mix up.
- Send progress messages, e.g. `{status: "loading-nltk"}`, so the page can show loading states. The first load downloads several MB.

## MDN essentials
- `new Worker(url, { type: "module" })` must be same-origin. Communicate with `postMessage()` / `onmessage`. Data is copied using the structured clone algorithm, so send plain objects and arrays. Don't send `Map`s or proxies unless you have to: use `dict_converter: Object.fromEntries`.
- Handle errors with `worker.onerror` on the page side, and send `{error}` messages from the worker.
- Workers can call `fetch()` (used to load `nltk_data` zips and `nltk_layer.py`).
