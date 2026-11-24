# Virtual filesystem and NLTK data

Sources:
- https://pyodide.org/en/stable/usage/file-system.html
- https://pyodide.org/en/stable/usage/api/js-api.html (`pyodide.FS`, `pyodide.unpackArchive`)
- https://www.nltk.org/data.html (manual installation layout)

## pyodide.FS
- "Pyodide includes a file system provided by Emscripten... accessed through `pyodide.FS` which re-exports the Emscripten File System API."
- Docs examples:
  ```js
  pyodide.FS.writeFile("/hello.txt", "hello world!", { encoding: "utf8" });
  pyodide.FS.readFile("/hello.txt", { encoding: "utf8" });
  pyodide.FS.mkdirTree("/mnt");
  ```
- "The default file system used in Pyodide is MEMFS, which is a virtual in-memory file system. The data stored in MEMFS will be lost when the page is reloaded." That's fine for us, because the data is re-fetched and the browser caches the HTTP responses. `IDBFS` can persist data but isn't needed.

## pyodide.unpackArchive(buffer, format, options)
- "Unpack an archive into a target directory." `format` is one of the `shutil.unpack_archive()` formats: `'zip'`, `'tar'`, `'gztar'`, `'bztar'`, `'wheel'`. Set the target with `options.extractDir`.

## Mounting NLTK data (project recipe)
NLTK expects `nltk_data/<category>/<package>` (nltk.org/data.html). The build copies these zips into `site/nltk_data/` from the official NLTK data packages:
```js
async function mountNltkData(py) {
  const pkgs = [
    ["sentiment", "vader_lexicon"],   // VADER reads it from inside the zip
    ["corpora",   "stopwords"],
    ["tokenizers","punkt_tab"],       // only if sent_tokenize/word_tokenize are used
  ];
  for (const [cat, name] of pkgs) {
    const buf = await (await fetch(`/nltk_data/${cat}/${name}.zip`)).arrayBuffer();
    py.FS.mkdirTree(`/nltk_data/${cat}`);
    py.FS.writeFile(`/nltk_data/${cat}/${name}.zip`, new Uint8Array(buf));  // keep zip (VADER path uses it)
    if (cat !== "sentiment") py.unpackArchive(buf, "zip", { extractDir: `/nltk_data/${cat}` });
  }
  await py.runPythonAsync(`import nltk; nltk.data.path.insert(0, "/nltk_data")`);
}
```
- Load our own module the same way: fetch `/py/nltk_layer.py`, `py.FS.writeFile("/home/pyodide/nltk_layer.py", src)`, then `import nltk_layer`. `/home/pyodide` is Pyodide's default working directory, which is on `sys.path`. If unsure, add the directory to `sys.path` explicitly.
- **Never call `nltk.download()` in Pyodide.** The `ssl` module is a stub (see type-conversions-and-limits.md), and network calls must go through browser fetch.
