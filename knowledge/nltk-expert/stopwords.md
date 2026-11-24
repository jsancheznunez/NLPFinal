# NLTK stopwords

Source: https://www.nltk.org/howto/corpus.html ("Word Lists and Lexicons")

## API (from the docs)
```python
>>> from nltk.corpus import names, stopwords, words
>>> stopwords.fileids()
['arabic', 'azerbaijani', 'bengali', 'danish', 'dutch', 'english', 'finnish', 'french', ...]
>>> sorted(stopwords.words('portuguese'))
['a', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', ...]
```
- The `stopwords` corpus is a **word-list corpus**, part of NLTK data. Download it with `nltk.download('stopwords')`. Files are stored under `nltk_data/corpora/stopwords/`.
- `stopwords.words('english')` returns a list of lowercase function words, including negations such as `not`, `no`, `nor`, `don't`, `isn't` and `wasn't`.
- The collocations HOWTO uses it as a word filter:
  `finder.apply_word_filter(lambda w: len(w) < 3 or w.lower() in nltk.corpus.stopwords.words('english'))`

## Project rules (from docs/01-nltk.md)
1. Convert the list to a `set` once at import time. `words()` returns a list, and `in` on a list is slow.
2. **Remove negations from the stopword set.** They carry sentiment and form complaint phrases ("not worth").
3. **Add domain noise words:** `product, item, amazon, bought, buy, ordered, order, one, get, would, really, also`.
4. Apply stopwords **only** to frequency and collocation features. **Never** strip them before VADER, which relies on negations, boosters and punctuation.
```python
from nltk.corpus import stopwords
NEGATIONS = {"not","no","nor","never","don't","doesn't","isn't","wasn't","won't","can't","couldn't"}
DOMAIN = {"product","item","amazon","bought","buy","ordered","order","one","get","would","really","also"}
STOP = (set(stopwords.words("english")) - NEGATIONS) | DOMAIN
```
