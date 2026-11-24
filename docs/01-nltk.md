# 01 — What NLTK Does Best for the Ecommerce Product Performance Analyzer

**Role in the app:** NLTK handles the **lexical and statistical layer**: tokenizing, stopword filtering, rule-based **sentiment (VADER)**, **word frequencies**, and **collocations** (phrases that appear together often, like "battery life" or "poor quality"). It is light, needs no trained model, and is the only one of the two libraries that runs in the browser through Pyodide out of the box (see [04-netlify-deployment.md](04-netlify-deployment.md)).

> Rule of thumb for the team: **NLTK answers "how often, how positive?"**. spaCy answers "what is it, and what is said about it?"

---

## 1. Tokenization

| Function | Use in the app |
|---|---|
| `nltk.sent_tokenize(text)` | Split a review into sentences so sentiment can be scored per sentence. Mixed reviews like "Love the color. Zipper broke in a week." are common. |
| `nltk.word_tokenize(text)` | Standard Treebank-style word tokens for frequency counts. Needs the `punkt_tab` resource. |
| `nltk.tokenize.TweetTokenizer(preserve_case=False, reduce_len=True)` | **Recommended for review text.** It keeps emoticons (`:)`), hashtags and contractions, and shortens elongations ("soooo" → "sooo"). Reviews read more like social posts than news. |
| `nltk.tokenize.RegexpTokenizer(r"\w+")` | Quick alphanumeric-only tokens for word clouds. No data download needed, so it is the safest choice inside Pyodide. |

```python
import nltk
nltk.download(["punkt_tab", "stopwords", "vader_lexicon", "wordnet"], quiet=True)
from nltk.tokenize import TweetTokenizer
tok = TweetTokenizer(preserve_case=False, reduce_len=True, strip_handles=True)
tokens = tok.tokenize("Sooo comfy!!! Runs small tho :(")
# ['sooo', 'comfy', '!', '!', '!', 'runs', 'small', 'tho', ':(']
```

## 2. Stopwords

- `nltk.corpus.stopwords.words("english")` has about 180 common function words.
- **Customize it for ecommerce.** Remove the negations from the stopword list (`not`, `no`, `nor`, `don't`, `isn't`, `wasn't`, …) because they flip meaning ("not worth it"). Add domain noise words: `product`, `item`, `amazon`, `bought`, `buy`, `ordered`, `one`, `get`, `would`, `really`.
- Use stopword removal **only** for frequency and collocation features. **Never strip stopwords before VADER**, because VADER needs negations, intensifiers ("very", "extremely") and punctuation.

```python
from nltk.corpus import stopwords
NEGATIONS = {"not", "no", "nor", "never", "don't", "doesn't", "isn't", "wasn't", "won't", "can't", "couldn't"}
DOMAIN = {"product", "item", "amazon", "bought", "buy", "ordered", "order", "one", "get", "would", "really", "also"}
STOP = (set(stopwords.words("english")) - NEGATIONS) | DOMAIN
```

## 3. VADER sentiment (the headline NLTK feature)

`nltk.sentiment.vader.SentimentIntensityAnalyzer` is a **lexicon- and rule-based** sentiment model tuned for short, informal, social-style text. It handles:
- **Negation** ("not good")
- **Intensifiers and dampeners** ("very good", "kind of good")
- **ALL CAPS** emphasis and **exclamation marks** ("GREAT!!!")
- **The contrastive "but"**: in "nice but flimsy", the clause after "but" gets more weight
- **Emoticons, emoji and slang** ("lol", ":)")

`polarity_scores(text)` returns `{neg, neu, pos, compound}`. `compound` is normalized to **[-1, 1]**. The standard thresholds from the VADER authors are:

| compound | label |
|---|---|
| ≥ 0.05 | positive |
| ≤ −0.05 | negative |
| otherwise | neutral |

```python
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()
sia.polarity_scores("The fabric is NOT great, but the fit is perfect!!")
# compound > 0 because the clause after "but" is weighted more
```

**How the analyzer uses it:**
1. **Per review and per sentence.** Score each sentence and keep the review's mean, minimum and maximum. A minimum below −0.5 inside a 5★ review is a "hidden complaint" signal.
2. **Rating vs. sentiment mismatch.** Flag reviews where `rating ≥ 4` but `compound ≤ −0.05`, or `rating ≤ 2` but `compound ≥ 0.5`. Sarcasm, wrong-star mistakes and mixed reviews are interesting cases to show in the demo.
3. **Product-level sentiment.** Average `compound` per `parent_asin`, plus % positive, % neutral and % negative. This average feeds the product performance score (see [03-dataset.md](03-dataset.md)).
4. **Sentiment over time.** Average `compound` by month from the review `timestamp` shows whether a product is improving or declining.
5. **Evaluation.** Treat star ratings as weak labels (1–2 = negative, 3 = neutral, 4–5 = positive) and report VADER's accuracy, macro-F1 and confusion matrix against them. This gives the report a real evaluation section.

**Limitations to document in the report:** VADER is English-only, misses sarcasm, and doesn't know domain-specific words ("runs small" is negative for clothes, but VADER scores it neutral). The lexicon is a plain `dict` (`sia.lexicon`), so you can update it with a few domain terms, e.g. `{"flimsy": -2.0, "runs small": ...}`. VADER scores single tokens only, so phrases have to go through collocations or spaCy rules instead.

## 4. Frequency analysis

- `nltk.FreqDist(tokens)`: the top-N words per product, per category, and per sentiment class. For example, "top words in negative reviews of Product X" shows the main complaints.
- `nltk.ConditionalFreqDist((label, word) ...)`: compares word frequencies across conditions such as positive vs. negative, or 1★ vs. 5★.
- **Lemmatize before counting** so "batteries" and "battery" merge. NLTK's `WordNetLemmatizer` works, but **spaCy lemmas are better** because they use POS context. In the hybrid pipeline, count spaCy lemmas with NLTK's `FreqDist`.
- Output for the UI: a bar chart of the top 20 terms per sentiment, plus a "trending terms" list comparing this period's frequency with the previous period's.

## 5. Collocations (multi-word phrases)

`nltk.collocations` finds word pairs and triples that co-occur more often than chance. In reviews these are often product aspects or complaint phrases: "battery life", "customer service", "true to size", "fell apart", "waste of money".

```python
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures

words = [w for w in tokens if w.isalpha() and w not in STOP]
bf = BigramCollocationFinder.from_words(words)
bf.apply_freq_filter(5)                      # ignore rare pairs; PMI over-rewards them
top_pmi   = bf.nbest(BigramAssocMeasures.pmi, 20)
top_llr   = bf.nbest(BigramAssocMeasures.likelihood_ratio, 20)  # more robust on small corpora
```

- **Association measures:** `pmi`, `likelihood_ratio`, `chi_sq`, `student_t`, `raw_freq`. Use **likelihood ratio** or **PMI with a frequency filter**, and say which in the report.
- **Split by sentiment.** Collocations from negative reviews give a list of complaint themes. Collocations from positive reviews give selling points. Both feed the "Opportunities" panel, e.g. "Improve: zipper quality; Market: true to size".
- `nltk.ngrams(tokens, n)` and `nltk.everygrams` give plain n-gram counts when association scores aren't needed.

## 6. Other NLTK pieces worth knowing (optional)

| Feature | Possible use |
|---|---|
| `nltk.NaiveBayesClassifier` | A small supervised sentiment baseline trained on star-rating labels. Compare it against VADER in the report. |
| `nltk.Text(tokens).concordance("zipper")` | Keyword-in-context view in a "drill into a term" UI. |
| `nltk.corpus.wordnet` | Synonym expansion for aspect keywords (e.g. "price" ≈ "cost" ≈ "value"). |
| `nltk.pos_tag` | Usable, but **use spaCy for POS**: it is more accurate and already computed. |

## 7. NLTK data resources

Download these at **build time**, or put them in the repo, so the deployed app never calls `nltk.download()` at runtime:

| Resource | Needed for |
|---|---|
| `punkt_tab` | `word_tokenize`, `sent_tokenize` (NLTK ≥ 3.8.2 uses `punkt_tab` instead of `punkt`) |
| `stopwords` | stopword list |
| `vader_lexicon` | VADER |
| `wordnet` (+ `omw-1.4`) | WordNet lemmatizer and synonyms (optional) |

Set the `NLTK_DATA` environment variable to point at a project folder (e.g. `./nltk_data`) so builds can find the resources and reproduce the same results.

**In the browser (Pyodide):** Pyodide ships NLTK (3.9.4 in the current stable release), but `nltk.download()` won't work normally there. Fetch the needed data files (e.g. `vader_lexicon.zip`) as static assets from your own Netlify site, write them into Pyodide's virtual filesystem, and add that path to `nltk.data.path`. Details are in [04-netlify-deployment.md](04-netlify-deployment.md).

## Sources
- NLTK documentation: https://www.nltk.org/ (API: `nltk.sentiment.vader`, `nltk.collocations`, `nltk.tokenize`)
- Hutto, C.J. & Gilbert, E. (2014). *VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text.* ICWSM.
- Pyodide built-in packages (lists `nltk 3.9.4`): https://pyodide.org/en/stable/usage/packages-in-pyodide.html
