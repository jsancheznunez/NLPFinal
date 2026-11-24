---
name: review-text-cleaning
description: "Clean and normalize customer review text consistently across the pipeline. Use before tokenizing, parsing, counting or scoring review text."
user-invocable: false
metadata:
  skill-id: S10
  shared-by: "data-engineer, nltk-expert, spacy-expert, metrics-engineer, build-pipeline-engineer"
---

# Review-text cleaning & normalization (S10)

Shared by: `data-engineer`, `nltk-expert`, `spacy-expert`, `metrics-engineer`, `build-pipeline-engineer`. Matrix: `docs/expert-roster.md` §3.

- Input text = `title + ". " + text`. Strip HTML tags and `<br />`, unescape HTML entities, and collapse whitespace.
- **Keep** case, punctuation, emoticons and negations for VADER. VADER uses caps, "!!!" and "not".
- Truncate to 2,000 characters before spaCy parsing. Drop empty texts.
- For frequency and collocation features only: lowercase, alphabetic tokens, the custom stopword set (negations kept; domain noise like "product", "amazon", "bought" removed).
- Strip `#` from hashtags before VADER, because NLTK notes "#BAD is neutral".
- One shared `clean_text()` in `analyzer/` used by both the build and Pyodide. No regex differences between environments.
