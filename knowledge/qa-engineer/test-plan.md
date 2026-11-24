# Project test plan

| Layer | Tests | Tool | Runs where |
|---|---|---|---|
| nltk_layer | stopword set keeps negations; VADER labels at ±0.05 on golden sentences; collocations exclude stopwords; module imports without `nltk.download` | pytest + parametrize | local / CI |
| spacy_layer | aspect-opinion pairs on golden sentences (amod, acomp+nsubj, neg); EntityRuler tags seeded brands as BRAND; noun-chunk normalization | pytest (session `nlp` fixture) | local / CI |
| metrics | Bayesian rating formula; z-score weights add up to 1; opportunity flags on a synthetic table | pytest | local / CI |
| pipeline | `build_analysis.py` on the `tests/fixtures` sample writes every expected file; JSON parses with `allow_nan=False`; schema-valid; deterministic (two runs are byte-identical) | pytest + `tmp_path` | local / CI |
| site | dashboard renders charts with real data; every canvas has `role="img"` + `aria-label`; no console errors; no horizontal scroll at 360px | Playwright | Deploy Preview URL |
| playground | the paste-a-review flow returns compound/pos/neu/neg within 60 s on cold load; the same text gives the same compound (±1e-4) as the build's `nltk_layer` | Playwright + pytest | Deploy Preview URL |
| budget | build time per stage < budget; `site/` total size < 10 MB; `site/data` < 5 MB | pytest / script | local + Netlify log |
