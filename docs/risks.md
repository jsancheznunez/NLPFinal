# Risk register

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Netlify build cannot reach raw.githubusercontent.com (NLTK data) or GitHub Releases (spaCy model wheel) | Low | Build fails | Both hosts are standard on Netlify. Fallback: commit `nltk_data/` (about 4.5 MB) and set `NLTK_DATA_DIR`. | build-pipeline-engineer |
| Build time grows past the plan's limit | Low | Build fails | Full build takes about 51 s locally (spaCy 34 s); the budget check fails at 600 s (`BUILD_BUDGET_SECONDS`). Shrink the sample if needed. | build-pipeline-engineer |
| Production deploy credits (15 per deploy, 300 a month on Free) | Medium | Deploys blocked for the month | Merge to `main` only at milestones; test on free Deploy Previews. | orchestrator |
| NLTK version drift between build and Pyodide | Low | Browser and build scores differ | `nltk==3.9.4` pinned; Playwright parity test (<= 1e-4). Re-check when Pyodide is upgraded. | nltk-expert / pyodide-engineer |
| Pyodide cold load (several MB from jsDelivr) | Medium | Slow first use of the playground | Loading runs in a module worker with progress messages; the CDN is browser-cached afterwards. | pyodide-engineer |
| jsDelivr unavailable (Chart.js, Pyodide) | Low | Charts and playground unavailable | Every chart has a data-table fallback; the playground reports the error. | frontend-engineer |
| Dataset license (none declared) | Medium | Reuse restrictions | Small sample, academic and non-commercial use only, citation on every page. | data-engineer |
| VADER weak on complaints and 3-star reviews (negative recall 0.53, neutral F1 0.10 on the Grocery sample) | Certain | Sentiment under-reports problems | Documented in docs/evaluation.md; aspects and collocations add context; small domain lexicon. | eval-report-writer |
| `en_core_web_sm` NER mistakes (e.g. common words tagged as NORP or ORG) | Certain | Noisy entity lists | The EntityRuler adds BRAND/PRODUCT patterns; limitations are documented. | spacy-expert |
| Local Playwright version must match the installed Chromium | Medium | e2e tests cannot start | `requirements-dev.txt` pins 1.63.0 (Chromium 1243); otherwise run `playwright install chromium`. | qa-engineer |
| Local Python differs from Netlify's 3.12 | Low | Untested runtime | The venv was built with Python 3.12.3. | build-pipeline-engineer |
