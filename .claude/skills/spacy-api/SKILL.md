---
name: spacy-api
description: "Exact spaCy APIs used by the analyzer: spacy.load, nlp.pipe, components, lemmas, dependency parse, noun chunks, NER, EntityRuler, PhraseMatcher, DependencyMatcher, displaCy. Use whenever writing or reviewing spaCy code."
user-invocable: false
metadata:
  skill-id: S13
  shared-by: "spacy-expert, eval-report-writer"
---

# spaCy API (S13)

Shared by: `spacy-expert`, `eval-report-writer`. Matrix: `docs/expert-roster.md` §3.

- Model: `en_core_web_sm` 3.8.0 (12 MB; pipeline `tok2vec, tagger, parser, attribute_ruler, lemmatizer, ner`; requires `spacy>=3.8.0,<3.9.0`), installed through a direct wheel URL in `requirements.txt`.
- Batch: `nlp.pipe(texts, batch_size=256)`, which returns a generator. Use `as_tuples=True` to carry review IDs. Use `disable=[...]` for passes that need less.
- Don't disable `tagger`/`attribute_ruler` if you need lemmas: "The rule mode requires Token.pos".
- Parse: `token.dep_`, `token.head`, `token.children`. Iterate "from below". `doc.noun_chunks` and `doc.sents` need the parser.
- Entities: `doc.ents`, `ent.label_`. Add `nlp.add_pipe("entity_ruler", before="ner", config={"phrase_matcher_attr": "LOWER"})` with BRAND patterns from metadata `store`.
- PhraseMatcher patterns are built with `nlp.make_doc(text)`.
- displaCy: `displacy.render(docs, style="dep"|"ent", page=True, options=...)` writes static files. Never `serve()`.
Details: `knowledge/spacy-expert/`.
