# Loading precomputed JSON

Source: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch

- MDN's basic pattern:
  ```js
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Response status: ${response.status}`);
  }
  const result = await response.json();
  ```
- "The promise returned by `fetch()` will reject on some errors, such as a network error or a bad scheme. However, if the server responds with an error like `404`, then `fetch()` fulfills with a `Response`". **Always check `response.ok`.**
- `Response.ok` "returns `true` if the status is in the 200 range."

## Project rules
- Use one helper, `loadJSON(path)`, that wraps the MDN pattern and shows a visible error state ("Couldn't load product data") instead of a blank chart.
- Use relative paths (`data/summary.json`) so pages work on Deploy Preview URLs and locally with `python -m http.server -d site`.
- Load `summary.json` and `products.json` on the dashboard, and `product/<parent_asin>.json` only on product pages. Keep the first page load small.
- Never compute NLP in the main page script. Live analysis goes through the Pyodide worker (pyodide-engineer).
