# 04 — Netlify: What It Can and Cannot Run, and the Recommended Architecture

**Bottom line:** Netlify **cannot run a Python server or Python serverless functions**. It **can** run Python **during the build**, and it serves static files that can run Python **in the visitor's browser** through Pyodide (NLTK yes, spaCy no). The architecture below is designed around those three facts.

---

## 1. Capability matrix

| Netlify feature | Runs Python? | Details (as of Nov 2026) |
|---|---|---|
| **Build step** (`[build] command`) | ✅ **Yes** | The build image is Ubuntu 24.04 ("Noble"). Python 3.x is preinstalled. Pin the version with the `PYTHON_VERSION` env var, a `runtime.txt` (bare version like `3.12`, **not** `python-3.12.x`), or a `Pipfile`. A `requirements.txt` in the base directory is installed with `pip` automatically. NLTK + spaCy + `en_core_web_sm` all install and run here. |
| **Netlify Functions** (serverless) | ❌ **No** | Supported languages: **TypeScript, JavaScript and Go only**. Functions run on AWS Lambda, Node.js runtime (default Node 24). Limits: **60 s** synchronous, **15 min** background, **30 s** scheduled; **1024 MB** memory by default (up to 4 GB on paid credit-based plans); **6 MB** buffered request/response (**20 MB** streamed, **256 KB** background payload); **~4 KB** total env vars. |
| **Edge Functions** | ❌ **No** | Deno runtime, TypeScript/JavaScript only. Meant for small, fast request handling at the edge. |
| **Static hosting (CDN)** | n/a (serves files) | HTML, JS, CSS, JSON, `.whl` and `.zip` files. This is how both the precomputed results and the Pyodide runtime reach the browser. |
| **Browser via Pyodide** | ✅ **Yes (in the visitor's browser)** | Pyodide (current stable: `314.0.8`) is CPython compiled to WebAssembly. Its built-in packages include **`nltk 3.9.4`**, `numpy 2.4.6`, `pandas 3.0.2`, `scikit-learn 1.8.0`, `regex`, `matplotlib`. **`spacy`, `thinc`, `blis`, `cymem`, `preshed`, `murmurhash`, `srsly` are NOT included**, and spaCy can't be installed with `micropip` because its dependencies are compiled C/Cython. |

### Things that can't work, so agents shouldn't try
- Flask, FastAPI or Django apps on Netlify. Netlify has no long-running server and no Python runtime for functions.
- `netlify/functions/analyze.py`. It won't be deployed, because Python isn't a Functions language.
- Running spaCy from a JS function (no Python there), or loading a Python model in a function bundle.
- Loading spaCy with `micropip.install("spacy")` in Pyodide. It fails on the compiled dependencies. The only browser demos (`spacy-wasm`) use hand-built wheels with `BLIS_ARCH=generic`, are unmaintained, and the request to add spaCy to Pyodide (pyodide/pyodide-recipes#179) has been open since 2020. **Not a safe base for a graded project.**
- Downloading the full Amazon dumps during the build. It is slow, flaky and could hit build time limits. Commit a sample instead (see [03-dataset.md](03-dataset.md)).

### Things that work well
- `pip install -r requirements.txt` + `python scripts/build_analysis.py` as the Netlify build command
- Writing precomputed JSON into the publish directory (e.g. `site/data/*.json`)
- Pyodide loaded from the jsDelivr CDN (`https://cdn.jsdelivr.net/pyodide/v<version>/full/pyodide.js`), with `await pyodide.loadPackage("nltk")`
- Serving the NLTK data files (`vader_lexicon.zip`, `stopwords.zip`, `punkt_tab.zip`) as static assets from the site, so Pyodide can mount them
- Optional TS Netlify Functions for non-Python tasks, e.g. a JSON search endpoint over the precomputed results. Not required.

---

## 2. Recommended architecture: "Build-time Python NLP + static dashboard + in-browser NLTK playground"

```
                ┌──────────────────────── Netlify build (Ubuntu 24.04, Python 3.12) ─────────────────────────┐
 git push ──▶   │ pip install -r requirements.txt   (nltk, spacy, en_core_web_sm wheel, pandas)              │
                │ python scripts/build_analysis.py                                                           │
                │   data/sample/reviews.jsonl + meta.jsonl                                                   │
                │     ├─ spaCy: nlp.pipe → lemmas, noun chunks, NER, dep-parse aspect/opinion pairs           │
                │     ├─ NLTK : VADER (review + sentence + aspect), FreqDist, collocations (on spaCy lemmas)  │
                │     └─ pandas: performance score, best-sellers, trends, opportunity flags                   │
                │   → site/data/summary.json, products.json, product/<asin>.json, aspects.json, trends.json   │
                │   → site/displacy/*.html (static spaCy visualizations)                                     │
                └───────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                            ▼  publish = "site"
                ┌──────────────────────────── Netlify CDN (static) ───────────────────────────────────────────┐
 browser ◀──────│ index.html + JS (charts) ── fetch("data/*.json")  → Dashboard, Product pages, Trends          │
                │ playground.html ── Pyodide + nltk (VADER, tokenize, FreqDist, collocations) on pasted text    │
                │                    + spaCy results shown from precomputed examples / displacy pages           │
                └───────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Why this design
1. **Both libraries run for real, in Python, unchanged.** The build runs the full NLTK + spaCy pipeline. The grader can read normal Python code (`scripts/`, `analyzer/`).
2. **It deploys on Netlify with no other services.** It doesn't need a Python server, so nothing exceeds the 60 s function limit and there are no cold starts.
3. **It is fast and free to host.** The dashboard is only static JSON and charts.
4. **It stays interactive.** The Pyodide playground lets a visitor paste their own review and get **live NLTK** output (VADER scores, tokens, top terms, collocations) in the browser. Pyodide's NLTK is the same library as at build time.
5. **It is honest about spaCy.** spaCy's results for the dataset are precomputed, and the dependency and entity visualizations are pre-rendered `displacy` HTML. The UI says: "spaCy analysis runs at build time; live analysis uses NLTK in your browser."

### Optional: live spaCy for pasted text
If the team decides live spaCy is required, the only reliable option is an **external Python API**, e.g. a small FastAPI on Hugging Face Spaces, Render or Fly.io. A Netlify Function would proxy to it, or the frontend would call it directly. This **breaks "everything on Netlify"** and adds hosting work, so keep it as an optional stretch goal that the app doesn't depend on.

---

## 3. Concrete config

**`netlify.toml`**
```toml
[build]
  command = "pip install -r requirements.txt && python scripts/build_analysis.py"
  publish = "site"

[build.environment]
  PYTHON_VERSION = "3.12"
  NLTK_DATA = "/opt/build/repo/nltk_data"   # or download into ./nltk_data in the script

# Pyodide needs no special headers for the basic single-threaded build.
[[headers]]
  for = "/data/*"
  [headers.values]
    Cache-Control = "public, max-age=3600"
```

**`requirements.txt`** (pin exact versions once tested locally)
```
nltk==3.9.*
spacy==3.8.*
en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
pandas
```

**In-browser NLTK (playground) sketch**
```html
<script src="https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.js"></script>
<script type="module">
  const py = await loadPyodide();
  await py.loadPackage("nltk");
  // Serve vader_lexicon.zip from our own site and unpack it into Pyodide's virtual filesystem
  const buf = await (await fetch("/nltk_data/sentiment/vader_lexicon.zip")).arrayBuffer();
  py.FS.mkdirTree("/nltk_data/sentiment");
  py.FS.writeFile("/nltk_data/sentiment/vader_lexicon.zip", new Uint8Array(buf));
  await py.runPythonAsync(`
import nltk; nltk.data.path.insert(0, "/nltk_data")
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()
  `);
  window.score = (t) => py.runPython(`sia.polarity_scores(${JSON.stringify(t)})`).toJs();
</script>
```
*Verify the exact Pyodide version string and CDN path on the Pyodide docs when implementing. Pyodide moved to a new version-numbering scheme, and the docs currently show `314.0.8`. A Web Worker is recommended so the UI doesn't freeze while Pyodide loads (~10 MB download, a few seconds on first visit).*

### Build budget notes
- Keep the build NLP step to a few minutes: sample about 10–50k reviews and run `nlp.pipe(batch_size=256)` with unused components disabled. Netlify builds have a time limit (15 minutes by default on most plans; *check the current plan limits in the Netlify UI*).
- To make deploys faster, run `build_analysis.py` locally or in GitHub Actions and commit `site/data/*.json`. Then make the Netlify build command a no-op or a check. **Keep the default where the Netlify build runs the pipeline**, because "deployed and computed on Netlify" fits the brief best. The committed-JSON path is a fallback if builds get slow.

---

## 4. Proposed repo layout (for the implementation agents)

```
netlify.toml
requirements.txt
data/sample/            reviews.jsonl, meta.jsonl  (committed, a few MB)
nltk_data/              (optional, committed NLTK resources for reproducible builds)
scripts/prepare_data.py   one-time: stream full .jsonl.gz → sample (NOT run on Netlify)
scripts/build_analysis.py Netlify build entrypoint → site/data/*.json
analyzer/
  nltk_layer.py         tokenize, stopwords, VADER, FreqDist, collocations
  spacy_layer.py        nlp.pipe, NER (+EntityRuler), noun chunks, lemmas, aspect/opinion pairs
  metrics.py            performance score, best-sellers, trends, opportunities
site/
  index.html, product.html, trends.html, playground.html, assets/…
  data/                 generated JSON (gitignored if built on Netlify)
  nltk_data/            zipped resources served to Pyodide
tests/                  pytest on tiny fixtures (Subscription_Boxes sample)
```

## Sources
- Netlify Functions: supported languages TypeScript/JavaScript/Go, limits table (https://docs.netlify.com/build/functions/overview/, https://docs.netlify.com/build/functions/get-started/, https://docs.netlify.com/build/functions/configuration/). Also confirmed through Netlify's official agent coding context (netlify-functions skill).
- Netlify build image Ubuntu 24.04, Python 3.x, `PYTHON_VERSION` / `Pipfile` / `runtime.txt` (https://docs.netlify.com/build/configure-builds/available-software-at-build-time/, https://docs.netlify.com/build/configure-builds/manage-dependencies/)
- Pyodide packages (stable 314.0.8: nltk 3.9.4, numpy 2.4.6, pandas 3.0.2, scikit-learn 1.8.0; no spaCy): https://pyodide.org/en/stable/usage/packages-in-pyodide.html
- spaCy in Pyodide: open request https://github.com/pyodide/pyodide-recipes/issues/179; community demo https://spacy.io/universe/project/spacy-wasm
