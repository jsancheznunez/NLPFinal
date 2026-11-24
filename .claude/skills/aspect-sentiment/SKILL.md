---
name: aspect-sentiment
description: "How spaCy and NLTK combine into aspect-based sentiment: spaCy finds (aspect, opinion, negated) pairs, VADER scores them, metrics aggregate them. Use for any sentiment, aspect or complaint-theme work."
user-invocable: false
metadata:
  skill-id: S14
  shared-by: "nltk-expert, spacy-expert, metrics-engineer, eval-report-writer"
---

# Sentiment & aspect-based sentiment analysis (S14)

Shared by: `nltk-expert`, `spacy-expert`, `metrics-engineer`, `eval-report-writer`. Matrix: `docs/expert-roster.md` §3.

Pipeline (the core NLTK + spaCy integration):
1. spaCy extracts (aspect lemma, opinion lemma, negated) using `amod`, `acomp` + `nsubj`, a `neg` child, `conj` sharing, and verb `dobj` (`knowledge/spacy-expert/linguistic-features.md`).
2. NLTK VADER scores the opinion phrase (prefixed with "not " if negated) or the containing sentence.
3. Aggregate per (product, aspect): mentions, mean compound, top opinions. Keep aspects with at least 3 mentions.
4. Review-level sentiment: sentence scores aggregated as mean, min and max. A 5★ review with a sentence min ≤ −0.5 is a "hidden complaint".
5. Mismatch flag: rating ≥ 4 and compound ≤ −0.05, or rating ≤ 2 and compound ≥ 0.5.
6. Evaluation: stars mapped to labels (1–2 neg, 3 neu, 4–5 pos), with macro-F1 as the headline (`knowledge/eval-report-writer/`).
Use the same thresholds (±0.05) in the build, the JSON and the Pyodide playground.
