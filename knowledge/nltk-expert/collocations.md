# Collocations

Sources:
- https://www.nltk.org/howto/collocations.html
- https://www.nltk.org/api/nltk.collocations.html
- https://www.nltk.org/api/nltk.metrics.association.html

"Collocations are expressions of multiple words which commonly co-occur."

## Finders
```python
import nltk
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder, QuadgramCollocationFinder
bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()

finder = BigramCollocationFinder.from_words(words)           # words: iterable of tokens
finder = BigramCollocationFinder.from_words(words, window_size=20)  # allow gaps between the words
finder = BigramCollocationFinder(word_fd, bigram_fd)          # or build from your own FreqDists
```
- `finder.nbest(measure, n)` returns the top n n-grams. `finder.score_ngrams(measure)` returns (ngram, score) pairs sorted by score. `finder.above_score(measure, min_score)` returns n-grams scoring above a threshold. `finder.ngram_fd` is the raw n-gram FreqDist.

## Filtering (from the HOWTO)
- PMI on its own favors rare pairs: "While these words are highly collocated, the expressions are also very infrequent. Therefore it is useful to apply filters, such as ignoring all bigrams which occur less than three times." Use `finder.apply_freq_filter(3)`.
- `finder.apply_word_filter(lambda w: len(w) < 3 or w.lower() in stopwords)` drops any n-gram that contains a matching word.
- `finder.apply_ngram_filter(lambda w1, w2, w3: 'and' in (w1, w3))` filters on the whole n-gram.
- "it is often important to remove low frequency candidates, as we lack sufficient evidence about their significance as collocations."

## Association measures (`nltk.metrics.association`)
`BigramAssocMeasures`, `TrigramAssocMeasures` and `QuadgramAssocMeasures` all inherit from `NgramAssocMeasures`, which provides `raw_freq`, `pmi`, `likelihood_ratio`, `chi_sq`, `student_t`, `poisson_stirling`, `jaccard`, `mi_like`. Bigram-only measures: `phi_sq`, `fisher`, `dice`. Measure functions take the marginals of a contingency table (bigram case: `n_ii, (n_ix, n_xi), n_xx`).

The HOWTO example combining a window, frequency filter, stopword filter and likelihood ratio:
```python
finder = BigramCollocationFinder.from_words(nltk.corpus.genesis.words('english-web.txt'), window_size=20)
finder.apply_freq_filter(2)
ignored_words = nltk.corpus.stopwords.words('english')
finder.apply_word_filter(lambda w: len(w) < 3 or w.lower() in ignored_words)
finder.nbest(bigram_measures.likelihood_ratio, 10)
```

## Project rules
- Input is spaCy lemmas, lowercase, alphabetic, with the custom stopword set (negations kept) filtered out.
- Use `apply_freq_filter(5)` on the full corpus and `(3)` per product, and score with `likelihood_ratio`. Report PMI as a secondary list. State the measure in the JSON and the report.
- Run it separately on positive and negative reviews: negative collocations are complaint themes and positive ones are selling points.
- Plain counts without association scores: `nltk.ngrams(tokens, n)`, `nltk.bigrams`, `nltk.trigrams`.
