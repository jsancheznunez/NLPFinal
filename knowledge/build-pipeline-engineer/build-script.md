# scripts/build_analysis.py on Netlify

Sources:
- https://docs.netlify.com/build/configure-builds/manage-dependencies.md (Netlify runs `pip install` on `requirements.txt` automatically)
- https://docs.netlify.com/build/configure-builds/overview.md ("Only files in the publish directory are deployed")
- https://docs.netlify.com/build/configure-builds/environment-variables.md (`CONTEXT`, `COMMIT_REF`)
- https://docs.python.org/3/library/json.html (`allow_nan`, `sort_keys`)

## Contract
- Netlify installs `requirements.txt`, then runs `python scripts/build_analysis.py` from the repo root, then publishes `site/`.
- The script must:
  1. Make sure the NLTK data exists in `$NLTK_DATA`. Either it's committed, or the script runs `python -m nltk.downloader -d $NLTK_DATA -q punkt_tab stopwords vader_lexicon` once if it's missing.
  2. Load `data/sample/*.jsonl`. Never download the full dataset.
  3. Run `analyzer.spacy_layer` (one `nlp.pipe` pass), then `analyzer.nltk_layer` (VADER, FreqDist, collocations), then `analyzer.metrics`.
  4. Validate each output against `schemas/*.schema.json` and **fail the build** (non-zero exit) on a schema error.
  5. Write `site/data/*.json` with `json.dumps(obj, ensure_ascii=False, allow_nan=False, separators=(",", ":"), sort_keys=True)`.
  6. Copy for the browser: `analyzer/nltk_layer.py` → `site/py/nltk_layer.py`, and the NLTK zips → `site/nltk_data/{sentiment,corpora,tokenizers}/*.zip`.
  7. Write `site/displacy/*` (from spacy-expert's helper).
  8. Write `site/data/build_info.json` with `COMMIT_REF`, `CONTEXT`, library versions, the sample size and timings per stage.
- Log the timing of each stage with `time.perf_counter()`. Fail loudly if the total goes over a budget, e.g. `BUILD_BUDGET_SECONDS=600`.

## Determinism
- No randomness in the build. Sampling happens in `prepare_data.py`.
- Sort lists before writing them, use stable tie-breakers (e.g. score, then `parent_asin`), and round floats to 4 decimals.
- Run the same command locally (`python scripts/build_analysis.py`) and check that `git diff site/data` is empty on a second run.
