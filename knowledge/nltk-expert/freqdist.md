# FreqDist

Source: https://www.nltk.org/api/nltk.probability.FreqDist.html

- `class nltk.probability.FreqDist(samples=None)`. "Bases: `Counter`". "A frequency distribution for the outcomes of an experiment... could be used to record the frequency of each word type in a document."
- Construction (docs):
  ```python
  >>> from nltk.tokenize import word_tokenize
  >>> from nltk.probability import FreqDist
  >>> fdist = FreqDist(word.lower() for word in word_tokenize('This is an example sentence'))
  ```
  or incrementally: `fdist[word.lower()] += 1`.
- Useful methods:
  - `N()`: "the total number of sample outcomes"
  - `B()`: number of bins (unique samples with count > 0)
  - `freq(sample)`: relative frequency (count / N)
  - `most_common(n)`: inherited from `Counter`. Use it for the top-N terms.
  - `max()`, `hapaxes()` (samples that occur once)
  - `update(...)` (invalidates the cached N), `copy()`, `tabulate()`, `pprint(maxlen=10)`, `plot(...)`. `plot` needs matplotlib, so **don't** call it in the build; export counts to JSON instead.
- Because it subclasses `Counter`, FreqDists can be added and subtracted, which is handy for comparing one period against another.
- `nltk.ConditionalFreqDist(pairs)` builds one FreqDist per condition, e.g. `((label, lemma) for ...)` for positive vs. negative vocabularies.

## Project rules
- Count **spaCy lemmas** with stopwords and punctuation filtered out. That gives cleaner counts than raw tokens.
- Output for JSON: `[{"term": t, "count": c, "freq": fd.freq(t)} for t, c in fd.most_common(20)]`.
- Trending terms: the change in `freq()` between the latest period and the previous one, using a minimum count to avoid noise.
