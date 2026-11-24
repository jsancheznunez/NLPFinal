# Knowledge: spacy-expert

Reference notes from the official spaCy documentation (spacy.io, plus its Markdown source at github.com/explosion/spaCy/website/docs) and the spacy-models release metadata. Read this index first, then the file for the task in hand.

| File | Covers | Main sources |
|---|---|---|
| [pipelines.md](pipelines.md) | `spacy.load`, components, `nlp.pipe`, disabling and excluding components, multiprocessing | spacy.io/usage/processing-pipelines |
| [en-core-web-sm.md](en-core-web-sm.md) | Model facts (version, size, components, labels, accuracy), install via `requirements.txt` | spacy.io/models/en, spacy.io/usage/models, spacy-models meta JSON |
| [linguistic-features.md](linguistic-features.md) | Lemmas, dependency parse navigation, noun chunks, entities, sentences | spacy.io/usage/linguistic-features, spacy.io/api/doc |
| [entity-ruler-and-matchers.md](entity-ruler-and-matchers.md) | EntityRuler, PhraseMatcher, DependencyMatcher | spacy.io/usage/rule-based-matching, spacy.io/api/entityruler |
| [displacy.md](displacy.md) | `displacy.render`, HTML/SVG export, options | spacy.io/usage/visualizers, spacy.io/api/top-level#displacy |

Project context: [docs/02-spacy.md](../../docs/02-spacy.md). **spaCy runs only in the Netlify Python build. It cannot run in Pyodide.**
