# VADER sentiment in NLTK

Sources:
- https://www.nltk.org/api/nltk.sentiment.vader.html
- https://www.nltk.org/howto/sentiment.html
- https://github.com/cjhutto/vaderSentiment (README.rst)

Citation required by the NLTK docs: Hutto, C.J. & Gilbert, E.E. (2014). *VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text.* ICWSM-14.

## API
- `nltk.sentiment.vader.SentimentIntensityAnalyzer(lexicon_file='sentiment/vader_lexicon.zip/vader_lexicon/vader_lexicon.txt')`. The lexicon is loaded through `nltk.data`, so the **`vader_lexicon`** data package must be installed (`nltk.download('vader_lexicon')`).
- `polarity_scores(text)` returns a dict `{'neg', 'neu', 'pos', 'compound'}`. The NLTK docs note: "Hashtags are not taken into consideration (e.g. #BAD is neutral)... we recommend preprocessing your data to remove the #."
- `sia.lexicon` is the word → valence dict built by `make_lex_dict()`. You can update it with domain words (valence scale −4 … +4).
- `VaderConstants` holds the rule tables:
  - `BOOSTER_DICT`, e.g. `'extremely': 0.293`, `'barely': -0.293`. `B_INCR = 0.293`, `B_DECR = -0.293`.
  - `C_INCR = 0.733`: the ALL-CAPS emphasis increment.
  - `N_SCALAR = -0.74`: the multiplier applied when a word is negated.
  - `NEGATE`: negation words (`not`, `never`, `isn't`, `wasn't`, `nothing`, `despite`, …).
  - `SPECIAL_CASE_IDIOMS`, e.g. `'yeah right': -2`, `'cut the mustard': 2`.
  - `normalize(score, alpha=15)`: "Normalize the score to be between -1 and 1 using an alpha that approximates the max expected value."

## Example from the NLTK sentiment HOWTO
```python
>>> from nltk.sentiment.vader import SentimentIntensityAnalyzer
>>> sid = SentimentIntensityAnalyzer()
>>> sid.polarity_scores("VADER is smart, handsome, and funny.")
compound: 0.8316, neg: 0.0, neu: 0.254, pos: 0.746
>>> sid.polarity_scores("VADER is smart, handsome, and funny!")
compound: 0.8439, neg: 0.0, neu: 0.248, pos: 0.752     # punctuation emphasis
>>> sid.polarity_scores("VADER is very smart, handsome, and funny.")
compound: 0.8545, neg: 0.0, neu: 0.299, pos: 0.701     # booster word
```
The HOWTO's test sentences also cover "kind of good" (dampener), "The plot was good, but the characters are uncompelling and the dialog is not great." (mixed, "but"), and "Sentiment analysis has never been good." (negation).

## What VADER handles (README)
Negations ("not good"), contractions as negations ("wasn't very good"), punctuation emphasis ("Good!!!"), ALL CAPS emphasis, degree modifiers (boosters "very", dampeners "kind of"), slang ("sux"), slang modifiers ("kinda", "friggin"), emoticons (":)"), UTF-8 emojis, and initialisms ("lol"). The lexicon has over 9,000 token features, each rated by 10 human raters on a −4 … +4 scale.

## Score meanings and thresholds (README, "About the Scoring")
- **`compound`**: "computed by summing the valence scores of each word in the lexicon, adjusted according to the rules, and then normalized to be between -1 (most extreme negative) and +1 (most extreme positive). This is the most useful metric if you want a single unidimensional measure of sentiment."
- Typical thresholds:
  - **positive:** `compound >= 0.05`
  - **neutral:** `-0.05 < compound < 0.05`
  - **negative:** `compound <= -0.05`
- **`pos` / `neu` / `neg`**: "ratios for proportions of text that fall in each category (so these should all add up to be 1... or close to it)."

## Project rules
- Score **sentences** (via `sent_tokenize` or spaCy `doc.sents`), then aggregate per review (mean, min, max). Also score whole reviews.
- For aspect pairs from spaCy, score the opinion phrase (prefix "not " if negated) or the containing sentence.
- Use the standard ±0.05 thresholds everywhere (build and Pyodide) so labels match.
- Build one `SentimentIntensityAnalyzer` and reuse it. Constructing one per sentence, as the HOWTO loop does, is slow.

## Project lexicon check (nltk 3.9.4 vader_lexicon, verified Nov 24 2026)
- **Missing** from the lexicon: flimsy, cheap, greasy, sticky, leaky, overpriced, smelly, soft, smooth, silky, sturdy, durable, moisturizing. **Present**: dead -3.3, broken -2.1, broke -1.8, defective -1.9, leaked -1.3, itchy -1.1, dull -1.7, gentle 1.9, flawless 2.3, okay 0.9.
- `nltk_layer.DOMAIN_LEXICON` adds the missing ones with `sia.lexicon.setdefault`, so VADER's own ratings are never changed. It is shared by the build and Pyodide. Effect on macro-F1: 0.500 → 0.507 (docs/evaluation.md).
- `punkt_tab.zip` is 4.3 MB (all languages). The build ships an English-only subset (`punkt_tab/english/`) to the browser. `PunktTokenizer("english")` only reads `tokenizers/punkt_tab/english/`.
