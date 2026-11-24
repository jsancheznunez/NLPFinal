# Expert Roster — Agents to Design, Build, Test and Deploy the Analyzer

**Locked decision:** everything runs on Netlify, with no outside servers.
- **Build time:** a Python step on Netlify runs NLTK + spaCy over the committed review sample and writes static JSON and HTML.
- **Runtime:** a static site serves the dashboard. An "Analyze your own review" page runs **NLTK live in the browser with Pyodide**. spaCy is **build-time only**, because Pyodide can't load it (see [04-netlify-deployment.md](04-netlify-deployment.md)).

So every role below maps to one of three places code actually runs: the **Python build step**, the **static site**, or **Pyodide in the browser**. None of the roles is for a backend server, database, Python Netlify Function or cloud ML service.

---

## 1. Roster at a glance

| # | Agent | ID | Phase | One-line job description |
|---|---|---|---|---|
| 1 | **Orchestrator** | `ORCH` | All | Splits the project into tasks, assigns them to agents in dependency order, enforces the interface contracts, and merges finished work toward a deployable `main`. |
| 2 | **Meta Agent** | `META` | All | Designs and improves the other agents: writes their prompts and skill files, checks their output against these docs, and updates the roster when a gap or overlap appears. |
| 3 | **Solution Architect** | `ARCH` | Design | Owns the build-time / static / Pyodide split, the repo layout, and the **JSON data contract** that connects the Python pipeline to the frontend. |
| 4 | **Data Engineer** | `DATA` | Build | Streams Amazon Reviews 2023, samples and cleans it into a committed `data/sample/`, and builds the tiny test fixtures. |
| 5 | **NLTK Expert** | `NLTK` | Build | Builds `analyzer/nltk_layer.py`: tokenization, ecommerce stopwords, VADER sentiment, FreqDist and collocations. Keeps the same code working in Pyodide. |
| 6 | **spaCy Expert** | `SPACY` | Build | Builds `analyzer/spacy_layer.py`: lemmas, NER with brand EntityRuler, noun-chunk aspects, dependency-based aspect-opinion pairs, and pre-rendered displaCy HTML. |
| 7 | **Analytics & Metrics Engineer** | `METRICS` | Build | Turns NLP output plus metadata into best-seller rankings, the performance score, trends and opportunity flags (`analyzer/metrics.py`). |
| 8 | **Build Pipeline Engineer** | `PIPE` | Build | Writes `scripts/build_analysis.py` and `requirements.txt` so the Netlify Python build runs the whole pipeline within its time budget and writes `site/data/*.json`. |
| 9 | **Frontend & Data-Viz Engineer** | `FE` | Build | Builds the static dashboard, product, trends and "How it works" pages that read the precomputed JSON and chart it accessibly. |
| 10 | **Pyodide / In-Browser NLP Engineer** | `PYO` | Build | Builds the "Analyze your own review" page: loads Pyodide + NLTK in a Web Worker, mounts the NLTK data files, and runs `nltk_layer` live on pasted text. |
| 11 | **Netlify Deployment Engineer** | `NET` | Deploy | Owns `netlify.toml`, build environment, caching headers, Deploy Previews and production deploys, and keeps the deploy credit cost low. |
| 12 | **QA & Test Engineer** | `QA` | Test | Writes pytest for the Python layers, browser tests (Playwright) for the static site and Pyodide page, and checks that JSON output matches the data contract. |
| 13 | **NLP Evaluation & Report Writer** | `EVAL` | Test / Deliver | Measures VADER and aspect quality against star ratings and hand labels, documents limitations, and writes the final project report and README. |

**Not on the roster, on purpose:** backend/API engineer, database administrator, cloud/MLOps engineer, Python-serverless engineer. The locked architecture has no runtime server, database or hosted model. Any proposal that needs one must go back to `ARCH` and `ORCH`.

---

## 2. Agent cards

Each card gives the agent's job, what it **owns** (files and outputs), its **inputs**, who it **hands off to**, and its **core skills**. Skill IDs match the matrix in section 3.

### 1. Orchestrator (`ORCH`)
- **Job:** Splits the project into tasks, assigns them to agents in dependency order, enforces the interface contracts, and merges finished work toward a deployable `main`.
- **Owns:** task plan and board, merge decisions, the definition of done for every task.
- **Inputs:** `docs/README.md`, this roster, status reports from every agent.
- **Hands off to:** everyone; it escalates design conflicts to `ARCH` and agent-quality problems to `META`.
- **Core skills:** S01, S02, S03, S04, S21.

### 2. Meta Agent (`META`)
- **Job:** Designs and improves the other agents: writes their prompts and skill files, checks their output against these docs, and updates the roster when a gap or overlap appears.
- **Owns:** agent prompt and skill files (e.g. `.claude/agents/*.md`, `.claude/skills/*`), this roster, the context pack each agent receives.
- **Inputs:** all docs, agent transcripts and outputs, QA failure reports.
- **Hands off to:** `ORCH` (updated roster and prompts); individual agents (revised instructions).
- **Core skills:** S01, S02, S03, S05, S06, S21.

### 3. Solution Architect (`ARCH`)
- **Job:** Owns the build-time / static / Pyodide split, the repo layout, and the JSON data contract that connects the Python pipeline to the frontend.
- **Owns:** `docs/architecture.md` (to be written), `schemas/*.schema.json` (data contract), the repo layout from [04-netlify-deployment.md](04-netlify-deployment.md).
- **Inputs:** docs 01–04, constraints from `NET` and `PYO`.
- **Hands off to:** `PIPE`, `FE`, `PYO`, `METRICS` (the contract); `QA` (contract tests).
- **Core skills:** S02, S03, S04, S07, S16, S17, S19.

### 4. Data Engineer (`DATA`)
- **Job:** Streams Amazon Reviews 2023, samples and cleans it into a committed `data/sample/`, and builds the tiny test fixtures.
- **Owns:** `scripts/prepare_data.py` (run locally, never on Netlify), `data/sample/*.jsonl`, `tests/fixtures/`, the data card (source, citation, no-license note, sampling method).
- **Inputs:** [03-dataset.md](03-dataset.md).
- **Hands off to:** `NLTK`, `SPACY`, `METRICS` (sample); `QA` (fixtures); `EVAL` (data card).
- **Core skills:** S07, S08, S09, S10, S20.

### 5. NLTK Expert (`NLTK`) — required
- **Job:** Builds `analyzer/nltk_layer.py`: tokenization, ecommerce stopwords, VADER sentiment, FreqDist and collocations. Keeps the same code working in Pyodide.
- **Owns:** `analyzer/nltk_layer.py`, the custom stopword list (keeps negations), VADER lexicon additions, the NLTK data list (`punkt_tab`, `stopwords`, `vader_lexicon`), and a **pure-Python, Pyodide-safe public API** (no `nltk.download()`, no file paths hard-coded).
- **Inputs:** [01-nltk.md](01-nltk.md), lemma stream from `SPACY`, sample from `DATA`.
- **Hands off to:** `METRICS` (sentiment and frequency outputs); `SPACY` (VADER scoring for aspect pairs); `PYO` (the same module for the browser); `EVAL` (VADER vs. stars).
- **Core skills:** S07, S10, S11, S12, S14, S15, S20.

### 6. spaCy Expert (`SPACY`) — required
- **Job:** Builds `analyzer/spacy_layer.py`: lemmas, NER with brand EntityRuler, noun-chunk aspects, dependency-based aspect-opinion pairs, and pre-rendered displaCy HTML.
- **Owns:** `analyzer/spacy_layer.py`, the `en_core_web_sm` model pin, `EntityRuler` patterns from metadata `store` names, `Matcher` issue phrases ("arrived damaged", "runs small"), `site/displacy/*.html`, the throughput budget (`nlp.pipe`, disabled components).
- **Inputs:** [02-spacy.md](02-spacy.md), sample and metadata from `DATA`.
- **Hands off to:** `NLTK` (lemmas for FreqDist/collocations); `METRICS` (aspects, entities); `FE` (displaCy pages); `PIPE` (runtime and memory profile).
- **Core skills:** S07, S10, S11, S13, S14, S16, S20.

### 7. Analytics & Metrics Engineer (`METRICS`)
- **Job:** Turns NLP output plus metadata into best-seller rankings, the performance score, trends and opportunity flags.
- **Owns:** `analyzer/metrics.py`: popularity proxies, Bayesian-adjusted rating, review velocity, the weighted performance score (weights shown in the UI), opportunity rules ("fix the top complaint", "under-marketed gem", "trending"), and the optional **clearly labeled simulated** `sales.csv`.
- **Inputs:** NLTK and spaCy outputs, metadata, the "no sales numbers" caveat in [03-dataset.md](03-dataset.md).
- **Hands off to:** `PIPE` (functions to call); `FE` (fields to show); `EVAL` (method write-up).
- **Core skills:** S07, S09, S10, S14, S17, S20.

### 8. Build Pipeline Engineer (`PIPE`)
- **Job:** Writes `scripts/build_analysis.py` and `requirements.txt` so the Netlify Python build runs the whole pipeline within its time budget and writes `site/data/*.json`.
- **Owns:** the build entrypoint, pinned Python dependencies (`nltk`, `spacy`, `en_core_web_sm` wheel, `pandas`), NLTK data setup via `NLTK_DATA`, JSON writers that validate against `ARCH`'s schemas, build timing logs, and the committed-JSON fallback if builds get too slow.
- **Inputs:** layer modules from `NLTK`, `SPACY`, `METRICS`; schemas from `ARCH`; build constraints from `NET`.
- **Hands off to:** `NET` (build command); `FE` (generated data); `QA` (pipeline to test).
- **Core skills:** S07, S08, S10, S16, S18, S19, S20.

### 9. Frontend & Data-Viz Engineer (`FE`)
- **Job:** Builds the static dashboard, product, trends and "How it works" pages that read the precomputed JSON and chart it accessibly.
- **Owns:** `site/*.html`, `site/assets/` (JS/CSS, charting library from a CDN or vendored), best-seller table, sentiment and aspect charts, trend lines, opportunity cards, the "spaCy runs at build time; live analysis uses NLTK in your browser" notice, responsive and accessible layout.
- **Inputs:** JSON contract from `ARCH`, generated data from `PIPE`, displaCy HTML from `SPACY`.
- **Hands off to:** `PYO` (shared layout and styles); `QA` (pages to test); `NET` (publish directory).
- **Core skills:** S16, S17, S22, S23, S24.

### 10. Pyodide / In-Browser NLP Engineer (`PYO`)
- **Job:** Builds the "Analyze your own review" page: loads Pyodide + NLTK in a Web Worker, mounts the NLTK data files, and runs `nltk_layer` live on pasted text.
- **Owns:** `site/playground.html`, `site/assets/pyodide-worker.js`, the pinned Pyodide CDN version, serving `site/nltk_data/*.zip` and writing them into Pyodide's virtual filesystem, loading states and error handling, first-load time budget (~10 MB download).
- **Inputs:** `nltk_layer.py` from `NLTK` (copied into `site/` by `PIPE` at build time so the browser and build use **the same code**), layout from `FE`.
- **Hands off to:** `QA` (browser tests); `EVAL` (demo notes).
- **Core skills:** S11, S12, S15, S16, S22, S23, S24.

### 11. Netlify Deployment Engineer (`NET`)
- **Job:** Owns `netlify.toml`, build environment, caching headers, Deploy Previews and production deploys, and keeps the deploy credit cost low.
- **Owns:** `netlify.toml` (`command`, `publish = "site"`, `PYTHON_VERSION`, `NLTK_DATA`), `[[headers]]` for `/data/*` and `/nltk_data/*`, build cache, Deploy Previews per branch, the production-deploy policy (15 credits each on credit-based plans), the deploy checklist.
- **Inputs:** [04-netlify-deployment.md](04-netlify-deployment.md), build entrypoint from `PIPE`, publish directory from `FE`.
- **Hands off to:** `ORCH` (deploy status); `QA` (Deploy Preview URLs to test).
- **Core skills:** S04, S18, S19, S21, S24.

### 12. QA & Test Engineer (`QA`)
- **Job:** Writes pytest for the Python layers, browser tests (Playwright) for the static site and Pyodide page, and checks that JSON output matches the data contract.
- **Owns:** `tests/` (unit tests on fixtures, golden-output tests for VADER and aspect extraction, schema validation of `site/data/*.json`), Playwright tests against Deploy Previews (dashboard renders, playground returns VADER scores, no console errors), performance checks (build time, page weight).
- **Inputs:** every agent's output, fixtures from `DATA`, schemas from `ARCH`.
- **Hands off to:** `ORCH` (pass/fail gate); `META` (recurring agent mistakes); the agent that owns a failure (bug report).
- **Core skills:** S05, S11, S19, S20, S22, S24.

### 13. NLP Evaluation & Report Writer (`EVAL`)
- **Job:** Measures VADER and aspect quality against star ratings and hand labels, documents limitations, and writes the final project report and README.
- **Owns:** `docs/evaluation.md` (accuracy, macro-F1 and confusion matrix for VADER vs. star labels; precision of aspect-opinion pairs on ~100 hand-labeled sentences), the limitations section (sarcasm, domain words, proxy sales metrics, no live spaCy), the final README, report and demo script.
- **Inputs:** outputs of `NLTK`, `SPACY`, `METRICS`; data card from `DATA`.
- **Hands off to:** `ORCH` (deliverables).
- **Core skills:** S05, S06, S09, S11, S13, S14.

---

## 3. Skill matrix — who shares each skill

✅ = core skill for that agent.

| ID | Skill | ORCH | META | ARCH | DATA | NLTK | SPACY | METRICS | PIPE | FE | PYO | NET | QA | EVAL | # |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Coordination** |
| S01 | Task decomposition & dependency planning | ✅ | ✅ | | | | | | | | | | | | 2 |
| S02 | Reading and enforcing project docs/constraints (locked Netlify-only decision) | ✅ | ✅ | ✅ | | | | | | | | | | | 3 |
| S03 | Agent prompt / handoff design (context packs, definitions of done) | ✅ | ✅ | ✅ | | | | | | | | | | | 3 |
| S04 | Git workflow (branches, PR review, merging to `main`) | ✅ | | ✅ | | | | | | | | ✅ | | | 3 |
| S05 | Reviewing output for correctness & consistency with docs | | ✅ | | | | | | | | | | ✅ | ✅ | 3 |
| S06 | Technical writing (docs, reports, skill files) | | ✅ | | | | | | | | | | | ✅ | 2 |
| **Python & data** |
| S07 | Python 3.12 engineering (modules, typing, packaging) | | | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | | | | | | 6 |
| S08 | Large-file streaming & sampling (`.jsonl.gz`) | | | | ✅ | | | | ✅ | | | | | | 2 |
| S09 | pandas data wrangling & aggregation | | | | ✅ | | | ✅ | | | | | | ✅ | 3 |
| S10 | Review-text cleaning & normalization | | | | ✅ | ✅ | ✅ | ✅ | ✅ | | | | | | 5 |
| **NLP** |
| S11 | Core NLP concepts (tokens, sentences, POS, lemmas, n-grams) | | | | | ✅ | ✅ | | | | ✅ | | ✅ | ✅ | 5 |
| S12 | **NLTK API** (TweetTokenizer, stopwords, VADER, FreqDist, collocations, NLTK data) | | | | | ✅ | | | | | ✅ | | | | 2 |
| S13 | **spaCy API** (pipelines, `nlp.pipe`, NER, EntityRuler, noun chunks, dependency parse, Matcher, displaCy) | | | | | | ✅ | | | | | | | ✅ | 2 |
| S14 | Sentiment & aspect-based sentiment analysis | | | | | ✅ | ✅ | ✅ | | | | | | ✅ | 4 |
| S15 | Writing Pyodide-compatible Python (pure-Python, no downloads, virtual FS paths) | | | | | ✅ | | | | | ✅ | | | | 2 |
| **Contracts & build** |
| S16 | JSON data contract / JSON Schema design | | | ✅ | | | ✅ | | ✅ | ✅ | ✅ | | | | 5 |
| S17 | Product analytics metrics (best-seller proxies, scoring, trends) | | | ✅ | | | | ✅ | | ✅ | | | | | 3 |
| S18 | Netlify Python build step (build image, `PYTHON_VERSION`, `requirements.txt`, build cache, time budget) | | | | | | | | ✅ | | | ✅ | | | 2 |
| S19 | Netlify config & static hosting (`netlify.toml`, publish dir, headers, Deploy Previews, credits) | | | ✅ | | | | | ✅ | | | ✅ | ✅ | | 4 |
| S20 | Python testing (pytest, fixtures, golden outputs) | | | | ✅ | ✅ | ✅ | ✅ | ✅ | | | | ✅ | | 6 |
| S21 | Status reporting & risk tracking | ✅ | ✅ | | | | | | | | | ✅ | | | 3 |
| **Web (static site + browser)** |
| S22 | Static HTML/CSS/JS (no backend), fetch of static JSON | | | | | | | | | ✅ | ✅ | | ✅ | | 3 |
| S23 | Data visualization & accessible UI (charts, color, responsive layout) | | | | | | | | | ✅ | ✅ | | | | 2 |
| S24 | Browser performance & testing (Web Workers, page weight, Playwright) | | | | | | | | | ✅ | ✅ | ✅ | ✅ | | 4 |

### Shared-skill pairs that need to work closely

| Shared skill | Agents | Why it matters |
|---|---|---|
| S12 NLTK API + S15 Pyodide-compatible Python | `NLTK` ↔ `PYO` | The browser must run **the same** `nltk_layer.py` as the build. Neither should fork it. |
| S14 Sentiment & aspect-based sentiment | `NLTK` ↔ `SPACY` ↔ `METRICS` ↔ `EVAL` | spaCy finds (aspect, opinion) pairs, NLTK's VADER scores them, Metrics rolls them up, and Eval measures them. This is the main place the two libraries combine. |
| S16 JSON data contract | `ARCH` ↔ `PIPE` ↔ `FE` ↔ `PYO` ↔ `SPACY` | One schema keeps the build output and the static pages in sync. |
| S18/S19 Netlify build & config | `PIPE` ↔ `NET` | The build command, Python version and time budget have to agree. |
| S02/S03 Constraints & handoffs | `ORCH` ↔ `META` ↔ `ARCH` | They keep every agent inside "Netlify only, spaCy at build time, NLTK live in Pyodide". |

---

## 4. Workflow and order of work

```
Design:   ARCH (contract, layout) ──┐        META writes agent prompts from this roster
                                    ▼
Build:    DATA ─▶ SPACY ─▶ NLTK ─▶ METRICS ─▶ PIPE ─▶ site/data/*.json
                    │        └──────────────▶ PYO (same nltk_layer in browser)
                    └──▶ displaCy HTML ─▶ FE (dashboard reads JSON)
Test:     QA (pytest + schema checks on every PR; Playwright on Deploy Previews)
Deploy:   NET (Deploy Preview per PR → production deploy on milestone merges only)
Deliver:  EVAL (evaluation.md, report, README, demo)
Overseen by ORCH throughout; META reviews agent output and updates prompts/roster.
```

**Milestones and gates (enforced by `ORCH`)**
1. **Contract frozen:** `ARCH` publishes the schemas; `QA` has schema tests.
2. **Pipeline green locally:** `DATA` sample committed. `NLTK` and `SPACY` layers pass tests on fixtures. `PIPE` produces valid JSON in less than half the build budget.
3. **First Deploy Preview:** `NET` deploys, `FE` dashboard renders real data, `QA` Playwright passes.
4. **Playground live:** `PYO` runs NLTK in the browser on the Deploy Preview, using the same `nltk_layer.py` as the build.
5. **Production deploy and report:** `EVAL` numbers are in, limitations are documented, and `NET` runs the production deploy.

## 5. Ground rules for every agent
- Run nothing outside Netlify. Use no Python Netlify Functions and no external APIs at runtime.
- spaCy runs **only** at build time. NLTK runs at build time **and** in Pyodide, from the **same module**.
- Never download the full dataset during the Netlify build. Use the committed `data/sample/` only.
- Label sales figures as **proxies**, and label any generated sales data as **simulated**.
- Every generated JSON file must validate against `ARCH`'s schema before it ships.
- Cite Hou et al. 2024 (arXiv:2403.03952) wherever the dataset is described.
