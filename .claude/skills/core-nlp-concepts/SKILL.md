---
name: core-nlp-concepts
description: "Shared vocabulary of tokens, sentences, POS tags, lemmas, n-grams, dependency arcs, entities and sentiment for the analyzer. Use when explaining, designing or testing any NLP step."
user-invocable: false
metadata:
  skill-id: S11
  shared-by: "nltk-expert, spacy-expert, pyodide-engineer, qa-engineer, eval-report-writer"
---

# Core NLP concepts (S11)

Shared by: `nltk-expert`, `spacy-expert`, `pyodide-engineer`, `qa-engineer`, `eval-report-writer`. Matrix: `docs/expert-roster.md` §3.

- **Token / sentence:** the units for counting and scoring. NLTK uses Punkt and TweetTokenizer; spaCy uses its tokenizer plus `doc.sents`.
- **Lemma:** the base form ("batteries" → "battery"). Use spaCy's rule lemmatizer, which needs POS tags.
- **POS:** ADJ for opinion words, NOUN/PROPN for aspects.
- **Dependency arc:** head → child with a label. `amod` ("cheap zipper"), `acomp` + `nsubj` ("strap is flimsy"), `neg` ("not great"), `conj`.
- **Noun chunk:** a base noun phrase, used as a candidate product aspect.
- **Named entity:** a labeled span (ORG, PRODUCT, MONEY, DATE, GPE; plus our BRAND from the EntityRuler).
- **N-gram / collocation:** adjacent words; a collocation is a statistically associated n-gram (PMI, likelihood ratio).
- **Sentiment (VADER):** `compound` in [−1, 1]. Positive ≥ 0.05, negative ≤ −0.05.
Library specifics: `knowledge/nltk-expert/`, `knowledge/spacy-expert/`.
