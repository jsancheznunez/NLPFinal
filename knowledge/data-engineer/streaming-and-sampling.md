# Streaming and sampling large .jsonl.gz files

Sources:
- https://docs.python.org/3/library/gzip.html
- https://docs.python.org/3/library/json.html
- https://docs.python.org/3/library/random.html
- https://pandas.pydata.org/docs/reference/api/pandas.read_json.html

## gzip
- `gzip.open(filename, mode='rb', compresslevel=6, encoding=None, errors=None, newline=None)`: "Open a gzip-compressed file in binary or text mode." Use **`'rt'`** for text mode, which wraps the file in `io.TextIOWrapper`. Pass `encoding="utf-8"`.
- When writing `.gz` outputs, set `mtime=0` on `GzipFile` "to generate a compressed stream that does not depend on creation time". That keeps committed files byte-stable.

## json
- `json.loads(line)` reads one JSON Lines record at a time.
- On output, use `json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)` for compact, deterministic JSON. `sort_keys=True` "dictionaries will be outputted sorted by key".
- **`allow_nan=False`**: "serialization of out-of-range float values (nan, inf, -inf) will result in a ValueError, in strict compliance with the JSON specification." The default `True` writes `NaN`, which the browser's `JSON.parse` **rejects**. Always set it to False and convert NaN to `None` first.

## random (reproducible sampling)
- `random.seed(a)` initializes the generator. "By reusing a seed value, the same sequence should be reproducible from run to run." Note that "Most of the random module's algorithms and seeding functions are subject to change across Python versions", so record the Python version in the data card.
- `random.sample(population, k)`: "Return a k length list of unique elements chosen from the population sequence. Used for random sampling without replacement."
- Prefer a dedicated `rng = random.Random(42)` over the global generator.

## pandas.read_json for JSON Lines
- `lines=True`: "Read the file as a json object per line."
- `chunksize=N` (only with `lines=True`): "Return JsonReader object for iteration". Use it to stream big files.
- `compression='infer'` detects `.gz` from the file extension.
- `nrows=N` (only with `lines=True`) reads the first N lines, which is handy for tests.

## Sampling recipe (`scripts/prepare_data.py`, run locally, never on Netlify)
1. Pass 1 over the review file: count reviews per `parent_asin` with `collections.Counter`, streaming with `gzip.open(..., "rt")`.
2. Choose the top 300 products by review count, plus a random 50 from the long tail with `rng = random.Random(42)`, so the "under-marketed gem" logic has data.
3. Pass 2: keep up to 100 reviews per chosen product. Use reservoir sampling, or keep all and then `rng.sample`. Drop reviews whose `text` is empty.
4. Stream the metadata file and keep the rows for the chosen `parent_asin`s.
5. Write `data/sample/reviews.jsonl` and `data/sample/meta.jsonl` sorted by key, with `ensure_ascii=False`. Write `data/sample/DATACARD.md` with the source URLs, category, seed, counts, Python version and the citation.
6. Fixtures: 30 reviews from `Subscription_Boxes` in `tests/fixtures/`.
