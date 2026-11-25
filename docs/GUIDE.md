# Step-by-step guide

From a fresh clone to a live Netlify site. Each step lists a command and what you should see.

## 1. Set up locally

You need Git and Python **3.12** (the version the Netlify build uses).

```bash
git clone https://github.com/jsancheznunez/NLPFinal.git
cd NLPFinal
python3.12 -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

Check the pins: `python -c "import nltk, spacy; print(nltk.__version__, spacy.__version__)"` should print `3.9.4 3.8.x`.
NLTK must stay at 3.9.4, the version inside Pyodide 314.0.8, so the browser and the build give identical scores.

## 2. (Optional) Re-create the data sample

The sample in `data/sample/` is committed, so you can skip this step. To regenerate it:

```bash
python scripts/prepare_data.py --category Grocery_and_Gourmet_Food --skip-fixtures
```

This streams `Grocery_and_Gourmet_Food.jsonl.gz` (1.6 GB) and `meta_Grocery_and_Gourmet_Food.jsonl.gz` (0.3 GB) from mcauleylab.ucsd.edu into `data/raw/` (gitignored). It then keeps the top 150 products plus 50 random long-tail products, up to 60 reviews each (seed 42), and rewrites `data/sample/`. `--skip-fixtures` leaves the small test set in `tests/fixtures/` unchanged. Expected output:

```
sample: 11233 reviews, 200 products -> .../data/sample
```

To use another Amazon Reviews 2023 category, pass its name to `--category` (e.g. `All_Beauty`, the script's default), then update the domain word list `DOMAIN_LEXICON` in `analyzer/nltk_layer.py`, the example reviews (`CURATED`) in `scripts/build_analysis.py`, and the category name in the page footers in `site/*.html`. The build reads the category label from `data/sample/DATACARD.md`.

Never run this on Netlify. The build only reads the committed sample.

## 3. Build the analysis

```bash
python scripts/build_analysis.py
```

This is the same command Netlify runs. It:
1. downloads `vader_lexicon`, `stopwords` and `punkt_tab` once into `./nltk_data/`
2. runs spaCy over every review, then NLTK, then the pandas metrics
3. validates every output against `schemas/*.schema.json`, stopping with an error if one fails
4. writes `site/data/`, `site/displacy/`, `site/py/nltk_layer.py` and `site/nltk_data/`

The log ends with a line like `[build] total: 51.06s (budget 600s); 205 JSON files, 7 displaCy files, 14248 aspect pairs`.

## 4. Preview

```bash
python -m http.server 8000 -d site
```

Open http://localhost:8000. Check that:
- the Dashboard shows charts, and every panel has an **NLTK**, **spaCy**, **spaCy + NLTK** or **Metrics (proxy)** badge
- **Analyze your own review** loads Python in your browser (the first visit downloads several MB from jsDelivr), then scores your text. The example buttons show "Matches the build-time score".
- the **Resources** link in the header and footer opens the list of documentation links

## 5. Test

```bash
pytest tests --ignore=tests/e2e        # 66 tests: NLTK/spaCy layers, metrics, schemas, deterministic build
pytest tests/e2e --tracing off         # 14 Playwright tests in Chromium against a local server
SITE_URL=https://nlpfinal-product-analyzer.netlify.app pytest tests/e2e --tracing off   # same tests against the live site
```

On a new machine, run `python -m playwright install chromium` once first. `requirements-dev.txt` pins Playwright 1.63.0, so adjust the pin if your installed browsers come from a different version.

Optional: `python scripts/evaluate.py` regenerates `docs/evaluation.md` (VADER vs. star ratings).

## 6. Deploy to Netlify

1. Push your branch to GitHub.
2. Log in at https://app.netlify.com, then **Add new project → Import an existing project → GitHub**, and select `NLPFinal`.
3. Don't type any build settings. Netlify reads `netlify.toml`:
   ```toml
   [build]
     command = "python scripts/build_analysis.py"
     publish = "site"
   [build.environment]
     PYTHON_VERSION = "3.12"
   ```
   Netlify installs `requirements.txt` automatically (nltk 3.9.4, spaCy 3.8, the `en_core_web_sm` 3.8.0 wheel, pandas, jsonschema).
4. Click **Deploy**. In the deploy log, look for the `[build]` stage timings and `validated + wrote 205 JSON files`.
5. Open the site URL and repeat the checks from step 4.

### Day-to-day workflow
- Work on a branch and open a pull request. Netlify builds a free **Deploy Preview** for it.
- Merge to `main` only at milestones. Every production deploy costs **15 credits** (Free plan: 300 a month).
- If a build fails, the log names the stage and, for schema problems, the file and field.

## Troubleshooting
| Symptom | Fix |
|---|---|
| `LookupError: Resource vader_lexicon not found` | Run the build once (it downloads the NLTK data), or set `NLTK_DATA_DIR`. |
| Playground stuck on "Downloading the Python runtime" | The browser must reach `cdn.jsdelivr.net`. Check the console, an ad blocker or a corporate proxy. |
| Playground scores differ from the build | The build must use `nltk==3.9.4`. Rebuild so `site/py/nltk_layer.py` is current. |
| Charts missing but tables shown | Chart.js could not load from jsDelivr. The data tables remain available. |
