# Ecommerce Product Performance Analyzer — Research Docs

Background research for the NLP final project. These docs are the **shared context for the team of expert agents** that will build the app. Read this index first, then the doc for your area.

**The app:** analyzes products sold online using sales data, customer reviews and product information to identify **best-selling products**, evaluate **customer sentiment**, measure **product performance**, and discover **trends and opportunities**. It must use **both NLTK and spaCy**, and it must be **deployed on Netlify**.

## Documents

| # | Doc | One-line summary |
|---|---|---|
| 1 | [01-nltk.md](01-nltk.md) | NLTK = lexical and statistical layer: TweetTokenizer, ecommerce stopwords (keep negations), **VADER** sentiment, FreqDist, collocations |
| 2 | [02-spacy.md](02-spacy.md) | spaCy = linguistic structure layer: **NER** (brands, money, durations), **noun chunks** → aspects, **lemmas**, **dependency parse** → aspect-opinion pairs |
| 3 | [03-dataset.md](03-dataset.md) | **Amazon Reviews 2023 (All_Beauty)** reviews + metadata joined on `parent_asin`; CC0 Women's Clothing Reviews as backup; there are no real sales figures, so use proxy metrics |
| 4 | [04-netlify-deployment.md](04-netlify-deployment.md) | Netlify runs Python **only at build time**. Functions are TS/JS/Go only. Pyodide has NLTK but **not spaCy** → recommended architecture and config |
| — | [expert-roster.md](expert-roster.md) | The 13 agents (incl. Orchestrator, Meta, **NLTK Expert**, **spaCy Expert**) with job lines, agent cards and a shared-skill matrix |

## Key decisions (TL;DR for every agent)

1. **Division of labor between the libraries.** Both are used in every review's pipeline:
   - **spaCy:** tokens and **lemmas**, sentences, **NER** (+ `EntityRuler` seeded with brand names from metadata), **noun chunks** (aspects), **dependency rules** (`amod`, `acomp`+`nsubj`, `neg`) → (aspect, opinion, negated) triples.
   - **NLTK:** **VADER** scores for reviews, sentences and each aspect-opinion pair; **FreqDist** and **collocations** (PMI / likelihood ratio) over spaCy lemmas, split by sentiment; a stopword list customized for ecommerce.
   - The **combined output** is aspect-based sentiment per product, e.g. "color +0.62 (140), strap −0.55 (41) → fix the strap".
2. **Data:** commit a **sample** (about 300 products × up to 100 reviews) of Amazon Reviews 2023 `All_Beauty` to `data/sample/`. Never download the full dump on Netlify. Cite Hou et al. 2024 (arXiv:2403.03952).
3. **"Sales" metrics are proxies.** Use rating count, review velocity, Bayesian-adjusted rating, sentiment and aspect health, combined into a transparent weighted **performance score**. If needed, add an optional synthetic `sales.csv` that is *clearly labeled simulated*.
4. **Architecture:** **Netlify build runs the Python NLTK + spaCy pipeline → writes static JSON → static dashboard.** There is also an in-browser **Pyodide + NLTK playground** for live VADER, tokens and collocations on pasted text. spaCy is shown live only through pre-rendered `displacy` HTML and precomputed results.
5. **Don't build:** Python Netlify Functions (unsupported), a Flask or FastAPI server on Netlify (impossible), or `micropip install spacy` in Pyodide (fails). Live spaCy on user text is an optional stretch goal and needs an external Python host.

## Agent team

See **[expert-roster.md](expert-roster.md)** for the full roster: 13 agents with job lines, owned files, handoffs, a shared-skill matrix, milestones and ground rules.

## Open items to verify during implementation
- [x] Amazon Reviews 2023 license: confirmed **none declared** (no `license:` field on the HF card). Use it for academic, non-commercial work, with citation.
- [ ] Exact Pyodide CDN version path, after the switch to the `314.x` version scheme.
- [ ] Netlify build time limit on the team's plan (not published in the docs), and the end-to-end build time with the chosen sample size. Note that production deploys cost 15 credits each.
- [ ] Exact pinned versions of `spacy` and `en_core_web_sm` (they must be compatible) and `nltk`.

*Researched November 2026. Sources are listed at the bottom of each doc.*
