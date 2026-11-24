---
name: netlify-python-build
description: "Make the Python NLP pipeline run reliably inside Netlify's build: build image, PYTHON_VERSION, automatic requirements install, dependency cache, time budget. Use for requirements.txt, the build command or build failures."
user-invocable: false
metadata:
  skill-id: S18
  shared-by: "build-pipeline-engineer, netlify-engineer"
---

# Netlify Python build step (S18)

Shared by: `build-pipeline-engineer`, `netlify-engineer`. Matrix: `docs/expert-roster.md` §3.

- Build image: Ubuntu 24.04. Set `PYTHON_VERSION = "3.12"` in `[build.environment]`.
- Netlify **automatically runs `pip install`** on `requirements.txt` in the base directory, so the build command is just `python scripts/build_analysis.py`.
- Pins: `nltk==3.9.4`, `spacy>=3.8.0,<3.9.0`, `en_core_web_sm @ <3.8.0 wheel URL>`, pandas, jsonschema. Dev tools go in `requirements-dev.txt`.
- The dependency cache speeds up later builds. If a build fails strangely, "retry with a cleared build cache".
- Budget: log the time of each stage and fail if over `BUILD_BUDGET_SECONDS`. Keep the sample at 10–50k reviews. The fallback is to commit generated JSON.
- Only `site/` is deployed. Copy `nltk_layer.py` and the NLTK zips into it.
Details: `knowledge/netlify-engineer/build-image-and-python.md`, `knowledge/build-pipeline-engineer/`.
