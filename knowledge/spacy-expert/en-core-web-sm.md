# en_core_web_sm

Sources:
- https://spacy.io/models/en
- https://raw.githubusercontent.com/explosion/spacy-models/master/meta/en_core_web_sm-3.8.0.json
- https://raw.githubusercontent.com/explosion/spacy-models/master/compatibility.json
- https://spacy.io/usage/models (sections "Installation via pip" and "Downloading and requiring package dependencies")

## Facts (from meta JSON, version 3.8.0)
| Field | Value |
|---|---|
| Version | `3.8.0` (the only `en_core_web_sm` release listed for spaCy `3.8` in compatibility.json) |
| Requires | `spacy >=3.8.0,<3.9.0` |
| Size | 12 MB |
| Type / genre (models page) | vocabulary, syntax, entities; written web text (blogs, news, comments) |
| Active pipeline | `tok2vec, tagger, parser, attribute_ruler, lemmatizer, ner` |
| All components | the above plus `senter`, which is **disabled** by default |
| License | MIT (training data: OntoNotes 5, ClearNLP dependency conversion, WordNet 3.0) |
| NER labels | CARDINAL, DATE, EVENT, FAC, GPE, LANGUAGE, LAW, LOC, MONEY, NORP, ORDINAL, ORG, PERCENT, PERSON, PRODUCT, QUANTITY, TIME, WORK_OF_ART |
| Accuracy (meta) | token 0.999, POS tag 0.973, sentences F 0.907, dep UAS 0.918 / LAS 0.899, NER P/R/F 0.843/0.844/0.843 |

Use `spacy.explain("NORP")` and similar to get a label's description.

**There is no `BRAND` label.** Brands come out as ORG, PRODUCT or nothing, which is why the project adds an EntityRuler.

## Installing in an automated build (Netlify)
- spaCy docs: "if you're downloading pipeline packages as part of an automated build process, [`spacy download`] only adds an unnecessary layer of complexity. If you know which packages your application needs, you should be specifying them directly."
- "Because pipeline packages are valid Python packages, you can add them to your application's `requirements.txt`." pip's requirements format supports direct URLs:
  ```text
  spacy>=3.8.0,<3.9.0
  en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
  ```
  (The wheel URL above was checked and returns HTTP 200.)
- Pipeline downloads are hosted on GitHub Releases (github.com/explosion/spacy-models/releases). `spacy info en_core_web_sm --url` prints the URL of the latest compatible version.
- Load it with `spacy.load("en_core_web_sm")`, or `import en_core_web_sm; nlp = en_core_web_sm.load()`.
- PyPI's latest spaCy as of Nov 2026 is `3.8.18` (requires Python >=3.10, <3.16), which is compatible with `en_core_web_sm-3.8.0`.

## Other English models (for reference)
`en_core_web_md` / `_lg` add word vectors (Type: "vocabulary, syntax, entities, vectors"). `en_core_web_trf` is a transformer model. The project does not use them because of build time and size.
