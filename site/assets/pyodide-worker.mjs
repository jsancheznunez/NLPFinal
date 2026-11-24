// Module Web Worker running NLTK in the browser with Pyodide 314.0.8 (Python 3.14, nltk 3.9.4).
// Pyodide requires a module-type worker (pyodide.asm.mjs is an ES module).
// spaCy is NOT loaded here: it cannot run in Pyodide (no wasm builds of its compiled deps).
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.mjs";

const SITE = new URL("../", import.meta.url); // site root, works on Deploy Preview URLs and subpaths
const NLTK_ZIPS = [
  ["sentiment", "vader_lexicon", false], // VADER reads its lexicon from inside the zip
  ["corpora", "stopwords", true],
  ["tokenizers", "punkt_tab", true],
];

function status(stage, detail = "") {
  self.postMessage({ type: "status", stage, detail });
}

async function fetchBytes(path) {
  const res = await fetch(new URL(path, SITE));
  if (!res.ok) throw new Error(`Couldn't load ${path} (HTTP ${res.status})`);
  return new Uint8Array(await res.arrayBuffer());
}

const ready = (async () => {
  const t0 = performance.now();
  status("loading-pyodide", "Downloading the Python runtime (first visit: several MB, cached afterwards)");
  const py = await loadPyodide();
  status("loading-nltk", "Loading the nltk package");
  await py.loadPackage("nltk");
  status("mounting-data", "Mounting NLTK data (VADER lexicon, stopwords, Punkt)");
  for (const [cat, name, unpack] of NLTK_ZIPS) {
    const bytes = await fetchBytes(`nltk_data/${cat}/${name}.zip`);
    const dir = `/nltk_data/${cat}`;
    py.FS.mkdirTree(dir);
    py.FS.writeFile(`${dir}/${name}.zip`, bytes);
    if (unpack) py.unpackArchive(bytes, "zip", { extractDir: dir });
  }
  const src = await fetchBytes("py/nltk_layer.py");
  py.FS.mkdirTree("/home/pyodide");
  py.FS.writeFile("/home/pyodide/nltk_layer.py", src);
  await py.runPythonAsync(`
import sys, json
if "/home/pyodide" not in sys.path:
    sys.path.insert(0, "/home/pyodide")
import nltk
nltk.data.path.insert(0, "/nltk_data")
import nltk_layer
nltk_layer.analyze("warm up: good")  # loads VADER, stopwords and Punkt once
`);
  const info = JSON.parse(py.runPython(`json.dumps({"python": sys.version.split()[0], "nltk": nltk.__version__})`));
  info.pyodide = py.version;
  info.seconds = +((performance.now() - t0) / 1000).toFixed(1);
  self.postMessage({ type: "ready", info });
  return py;
})();

ready.catch((err) => self.postMessage({ type: "fatal", error: String(err && err.message ? err.message : err) }));

self.onmessage = async (event) => {
  const { id, text } = event.data;
  try {
    const py = await ready;
    py.globals.set("review_text", String(text));
    // json.dumps -> JSON.parse: plain objects, no PyProxy to destroy.
    const out = py.runPython("json.dumps(nltk_layer.analyze(review_text))");
    self.postMessage({ type: "result", id, result: JSON.parse(out) });
  } catch (err) {
    self.postMessage({ type: "result", id, error: String(err && err.message ? err.message : err) });
  }
};
