# Ecommerce Product Performance Analyzer (Customer Review Analyzer)

An NLP final project that analyzes online products from their customer reviews and product data. It finds **best-sellers** (through clearly labelled proxies), measures **customer sentiment** and **product performance**, and surfaces **trends and opportunities** such as "popular, but customers complain about the battery". It uses **both NLTK and spaCy** and deploys **only on Netlify**.

- Live pages: Dashboard, Products, Product detail, Aspects, Trends, **Analyze your own review** (live NLTK in the browser), How it works, [Resources](site/resources.html)
- Step-by-step guide: [docs/GUIDE.md](docs/GUIDE.md)
- Evaluation: [docs/evaluation.md](docs/evaluation.md) (VADER vs. stars: macro-F1 0.522 on 3 classes, 0.804 positive vs. negative)

## How NLTK and spaCy are used

Every result in the UI and in the JSON carries a library label: **NLTK**, **spaCy**, **spaCy + NLTK** (spaCy extraction scored by NLTK) or **Metrics (proxy)**.

| Library | Where it runs | What it does (file) |
|---|---|---|
| **spaCy** 3.8 + `en_core_web_sm` 3.8.0 | Netlify build only | `analyzer/spacy_layer.py`: one `nlp.pipe` pass for lemmas and sentences, **NER** with an **EntityRuler before `ner`** (BRAND patterns from metadata `store`, PRODUCT patterns from title heads), **noun chunks** as aspects ("battery life"), **dependency rules** (`amod`, `acomp`+`nsubj`, opinion verb + `dobj`, `conj`, `neg`) that yield (aspect, opinion, negated) pairs, and pre-rendered **displaCy** SVG/HTML |
| **NLTK** 3.9.4 | Netlify build **and** the browser (Pyodide) | `analyzer/nltk_layer.py`: **TweetTokenizer**, ecommerce **stopwords that keep negations**, **VADER** (±0.05 thresholds, plus a small domain lexicon), **FreqDist** top words, **bigram collocations** (likelihood ratio + frequency filter), and `analyze(text)` for the browser box |
| pandas | Netlify build | `analyzer/metrics.py`: best-seller proxy (`rating_number`), Bayesian rating, review velocity, weighted performance score, opportunity flags |

spaCy cannot run in the browser (Pyodide has no builds of its compiled dependencies), so the live box shows NLTK results only and says so. spaCy results exist for the precomputed dataset.

## Architecture

```
git push ─▶ Netlify build (Ubuntu 24.04, Python 3.12)
            pip install -r requirements.txt          (automatic)
            python scripts/build_analysis.py
              data/sample/*.jsonl ─▶ spaCy (nlp.pipe) ─▶ NLTK (VADER, FreqDist, collocations) ─▶ pandas metrics
              ─▶ validate against schemas/*.schema.json (fail the build on error), json allow_nan=False
              ─▶ site/data/*.json, site/data/product/<asin>.json, site/displacy/*,
                 site/py/nltk_layer.py, site/nltk_data/*.zip
            publish = "site"  ─▶ Netlify CDN (static only, no Functions, no servers)

browser ─▶ static pages + Chart.js 4.5.1 read site/data/*.json
        ─▶ playground.html ─▶ module Web Worker ─▶ Pyodide 314.0.8 (Python 3.14) + nltk 3.9.4
                               mounts site/nltk_data zips, imports site/py/nltk_layer.py (the same file as the build)
```

| Path | Contents |
|---|---|
| `data/sample/` | committed sample: 11,233 reviews of 200 Grocery_and_Gourmet_Food products, `meta.jsonl`, `DATACARD.md` |
| `analyzer/` | `nltk_layer.py`, `spacy_layer.py`, `metrics.py`, `contract.py` (schema validation) |
| `schemas/` | JSON Schema 2020-12 contract for every file in `site/data/` |
| `scripts/` | `prepare_data.py` (one-time sampling), `build_analysis.py` (Netlify build), `evaluate.py` |
| `site/` | the deployed static app (generated `data/`, `py/`, `nltk_data/`, `displacy/` are gitignored) |
| `tests/` | pytest (layers, metrics, schemas, pipeline determinism) and Playwright (`tests/e2e/`) |
| `netlify.toml` | build command, publish dir, Python 3.12, cache headers |

## Local setup

Requires Python 3.12 (the version Netlify uses).

```bash
git clone https://github.com/jsancheznunez/NLPFinal.git
cd NLPFinal
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt        # requirements.txt + pytest, Playwright, scikit-learn
```

## Run it

```bash
# 1. (optional) re-create the committed sample from mcauleylab.ucsd.edu (about 135 MB download, under a minute)
python scripts/prepare_data.py

# 2. build exactly as Netlify does (downloads NLTK data once into ./nltk_data)
python scripts/build_analysis.py

# 3. preview the static site
python -m http.server 8000 -d site          # open http://localhost:8000

# 4. tests
pytest tests --ignore=tests/e2e             # layers, metrics, schemas, determinism
pytest tests/e2e --tracing off              # Playwright: pages, labels, Resources link, Pyodide parity
#   (first time on a new machine: python -m playwright install chromium)

# 5. evaluation report (writes docs/evaluation.md)
python scripts/evaluate.py
```

A local build of the full sample takes about 45 s (spaCy about 35 s of that) and writes 205 JSON files.

## Deploy to Netlify

1. Push this repository to GitHub (it is at https://github.com/jsancheznunez/NLPFinal).
2. In Netlify: **Add new project → Import an existing project → GitHub**, then pick the repository.
3. Leave the build settings empty. **`netlify.toml` provides them**, and file settings override the UI:
   - build command `python scripts/build_analysis.py`
   - publish directory `site`
   - `PYTHON_VERSION = "3.12"`. Netlify installs `requirements.txt` with pip automatically, including the `en_core_web_sm` wheel from GitHub Releases.
4. Click **Deploy**. The build log shows each stage's timing (`[build] spacy: ...`) and fails if any JSON file breaks its schema.
5. **Deploy Previews:** every pull request gets a free preview URL. Test there with `SITE_URL=<preview-url> pytest tests/e2e --tracing off` (the same 14 Playwright tests, run against the deployed site; build locally from the same commit first so the playground scores can be compared).
6. **Live site:** https://nlpfinal-product-analyzer.netlify.app. Verified with `SITE_URL=https://nlpfinal-product-analyzer.netlify.app pytest tests/e2e --tracing off`, 14 passed. For docs- or test-only commits to `main`, put `[skip netlify]` in the commit message to skip the 15-credit production deploy.
6. **Credits:** on credit-based plans each **production deploy costs 15 credits** (Free plan: 300 credits a month), while Deploy Previews cost none. Merge to `main` only at milestones.

No environment variables, secrets, Functions or extra headers need to be set in the Netlify UI. Pyodide is loaded from the jsDelivr CDN, and no COOP/COEP headers are needed.

## Dataset, citation and license

Amazon Reviews 2023 (McAuley Lab), category Grocery_and_Gourmet_Food: https://amazon-reviews-2023.github.io/

> Hou, Y., Li, J., He, Z., Yan, A., Chen, X., & McAuley, J. (2024). *Bridging Language and Items for Retrieval and Recommendation.* arXiv:2403.03952.

**No license is declared** for the dataset, so this project uses a small sample for **academic, non-commercial purposes only**. There are **no sales figures** in the data: "best-seller" and velocity numbers are **proxies** (rating counts and review counts), and no simulated sales data is used. Details: [data/sample/DATACARD.md](data/sample/DATACARD.md).

Also cited: VADER (Hutto & Gilbert, ICWSM 2014), NLTK (Bird, Klein & Loper 2009), spaCy (Honnibal et al. 2020).

## More

- [docs/GUIDE.md](docs/GUIDE.md): the step-by-step guide
- Resources page (`site/resources.html`, linked in every page header and footer): every documentation link the project relies on
- [docs/](docs/README.md): research and design decisions; [docs/risks.md](docs/risks.md): risk register
- The agent team that built this: [CLAUDE.md](CLAUDE.md), [docs/expert-roster.md](docs/expert-roster.md)
