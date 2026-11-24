# NLTK tokenizers

Sources:
- https://www.nltk.org/api/nltk.tokenize.html
- https://www.nltk.org/api/nltk.tokenize.casual.html
- https://www.nltk.org/api/nltk.tokenize.punkt.html

## Recommended functions (`nltk.tokenize`)
- `nltk.tokenize.word_tokenize(text, language='english', preserve_line=False)`: "NLTK's recommended word tokenizer (currently an improved `TreebankWordTokenizer` along with `PunktSentenceTokenizer` for the specified language)." With `preserve_line=True` it does **not** sentence-split first.
- `nltk.tokenize.sent_tokenize(text, language='english')`: "using NLTK's recommended sentence tokenizer (currently `PunktSentenceTokenizer` for the specified language)."
- Example from the docs:
  ```python
  >>> s = '''Good muffins cost $3.88\nin New York.  Please buy me
  ... two of them.\n\nThanks.'''
  >>> word_tokenize(s)
  ['Good', 'muffins', 'cost', '$', '3.88', 'in', 'New', 'York', '.', 'Please', 'buy', 'me', 'two', 'of', 'them', '.', 'Thanks', '.']
  >>> sent_tokenize(s)
  ['Good muffins cost $3.88\nin New York.', 'Please buy me\ntwo of them.', 'Thanks.']
  ```
- Both functions need the **Punkt** data. Current NLTK loads Punkt parameters from the `punkt_tab` data package through `PunktTokenizer` (`nltk.tokenize.punkt.PunktTokenizer`: "Punkt Sentence Tokenizer that loads/saves its parameters from/to data files"). Download `punkt_tab`, not the legacy pickled `punkt`.

## Punkt
- "This tokenizer divides a text into a list of sentences by using an unsupervised algorithm to build a model for abbreviation words, collocations, and words that start sentences." The NLTK data package includes a pre-trained English model.
  ```python
  from nltk.tokenize import PunktTokenizer
  sent_detector = PunktTokenizer()          # English by default
  sent_detector.tokenize(text.strip())
  ```
- Punkt handles abbreviations such as "Mr." and "S." correctly. Review text has few of them, but don't replace it with a naive `split('.')`.

## TweetTokenizer (`nltk.tokenize.casual`), recommended for reviews
- "Twitter-aware tokenizer, designed to be flexible and easy to adapt to new domains and tasks."
- `TweetTokenizer(preserve_case=True, reduce_len=False, strip_handles=False, match_phone_numbers=True)`
  - `preserve_case=False`: "downcase everything except for emoticons."
  - `reduce_len=True`: "replace repeated character sequences of length 3 or greater with sequences of length 3."
  - `strip_handles=True`: removes `@handles`.
- Docs examples:
  ```python
  >>> TweetTokenizer().tokenize("This is a cooool #dummysmiley: :-) :-P <3 and some arrows < > -> <--")
  ['This', 'is', 'a', 'cooool', '#dummysmiley', ':', ':-)', ':-P', '<3', 'and', 'some', 'arrows', '<', '>', '->', '<--']
  >>> TweetTokenizer(strip_handles=True, reduce_len=True).tokenize('@remy: This is waaaaayyyy too much for you!!!!!!')
  [':', 'This', 'is', 'waaayyy', 'too', 'much', 'for', 'you', '!', '!', '!']
  ```
- **TweetTokenizer needs no data download.** It is regex-only, so it works in Pyodide without mounting `punkt_tab`.

## Other tokenizers in `nltk.tokenize`
- `RegexpTokenizer(pattern)`, e.g. `RegexpTokenizer(r"\w+")`, gives alphanumeric tokens only. It also needs no data.
- `wordpunct_tokenize(text)` splits on `\w+|[^\w\s]+`. The collocations HOWTO uses it in its examples.
- `TreebankWordTokenizer`, `ToktokTokenizer`, `MWETokenizer` (merges multi-word expressions like `("battery","life")` into one token).

## Project rules
- Build pipeline: lemmas usually come from spaCy. Use NLTK tokenizers for the Pyodide playground and any NLTK-only path.
- Playground: use `TweetTokenizer(preserve_case=False, reduce_len=True)`, plus `sent_tokenize` only if `punkt_tab` is mounted.
