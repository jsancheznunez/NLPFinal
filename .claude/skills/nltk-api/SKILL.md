---
name: nltk-api
description: "Exact NLTK APIs used by the analyzer: TweetTokenizer, word/sent_tokenize, stopwords, VADER, FreqDist, collocation finders and association measures, NLTK data paths. Use whenever writing or reviewing NLTK code."
user-invocable: false
metadata:
  skill-id: S12
  shared-by: "nltk-expert, pyodide-engineer"
---

# NLTK API (S12)

Shared by: `nltk-expert`, `pyodide-engineer`. Matrix: `docs/expert-roster.md` §3.

- Tokenize: `TweetTokenizer(preserve_case=False, reduce_len=True)` needs no data. `word_tokenize`/`sent_tokenize` need `punkt_tab`.
- Stopwords: `set(stopwords.words("english")) - NEGATIONS | DOMAIN` (`knowledge/nltk-expert/stopwords.md`).
- VADER: one `SentimentIntensityAnalyzer()`, then `polarity_scores(text)` returns `{neg, neu, pos, compound}`. Thresholds ±0.05. Needs `vader_lexicon` (read from the zip).
- Counts: `FreqDist(...).most_common(n)`, `.freq(t)`, `.N()`. Never `.plot()` in the build.
- Collocations: `BigramCollocationFinder.from_words(words)`, `.apply_freq_filter(5)`, `.apply_word_filter(...)`, `.nbest(BigramAssocMeasures.likelihood_ratio, 20)`.
- Data: `NLTK_DATA` env var or `nltk.data.path.insert(0, path)`. Download with `python -m nltk.downloader -d DIR -q punkt_tab stopwords vader_lexicon`. **Never** call `nltk.download()` in Pyodide.
- Version: `nltk==3.9.4`, the same as Pyodide.
