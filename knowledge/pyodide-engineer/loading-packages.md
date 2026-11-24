# Loading packages

Sources:
- https://pyodide.org/en/stable/usage/loading-packages.html
- https://pyodide.org/en/stable/usage/packages-in-pyodide.html
- https://github.com/pyodide/pyodide-recipes/issues/179

## Two ways to load packages
- "Only the Python standard library is available after importing Pyodide." To use other packages:
  - **`micropip.install()`** (Python): "for pure Python packages with wheels as well as Pyodide packages... It can install packages from PyPI, the JsDelivr CDN or from other URLs." Pure-Python wheels from any URL work, but "the server must set Cross-Origin Resource Sharing (CORS) headers." micropip checks wheel hashes against the PyPI JSON API.
  - **`pyodide.loadPackage()`** (JS): "for packages built with Pyodide... less overhead but also more limited functionality." It loads the dependencies of official packages, but there's "no dependency resolution when loading packages from custom URLs."
- The docs' advice: "use `micropip.install()` for everything except... to load micropip itself, [or] when you are optimizing for size, do not want to install the `micropip` package, and do not need to install packages from PyPI with dependency resolution."
- **Project choice: `await pyodide.loadPackage("nltk")`.** NLTK is an official Pyodide package, and `regex` loads automatically as a dependency. This avoids downloading micropip.
- `loadPackagesFromImports(code)` scans the imports in a code string and loads any matching Pyodide packages. It doesn't download from PyPI. The docs' worker example uses it. We call `loadPackage` explicitly instead, so loading is predictable.
- "In general, loading a package twice is not permitted." Load once at worker start-up.

## What is available (packages page, 314.0.8)
- Available: `nltk 3.9.4`, `regex 2026.3.32`, `numpy 2.4.6`, `pandas 3.0.2`, `scikit-learn 1.8.0`, `matplotlib 3.10.8`.
- **Not listed:** `spacy`, `thinc`, `blis`, `cymem`, `preshed`, `murmurhash`, `srsly`, `wasabi`, `catalogue`.
- spaCy depends on compiled C/Cython extensions that have no Pyodide build, so `micropip.install("spacy")` cannot work. The open request (pyodide-recipes#179, opened 2020) says a previous attempt "would need to continue". The only workaround is hand-built wheels with `BLIS_ARCH=generic`, which is unsupported. **Out of scope for this project.**

## Version-alignment rule
- The build must use the **same NLTK version as Pyodide**: pin `nltk==3.9.4` in `requirements.txt`. PyPI's latest is 3.10.x, which the browser doesn't have. Then VADER scores in the playground and in the precomputed JSON come from the same code and lexicon.
