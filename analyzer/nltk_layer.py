"""NLTK layer: tokens, ecommerce stopwords, VADER, FreqDist, collocations.

This file runs UNCHANGED in two places:
  * the Netlify build (CPython 3.12, nltk==3.9.4), called by scripts/build_analysis.py
  * the browser (Pyodide 314.0.8 = Python 3.14, nltk 3.9.4), loaded by
    site/assets/pyodide-worker.mjs from site/py/nltk_layer.py

Rules: stdlib + nltk (+ its regex dependency) only. Never call nltk.download();
the NLTK data (vader_lexicon, stopwords, punkt_tab) must already be on
nltk.data.path. Every float is rounded to 4 decimals so build and browser
outputs compare exactly.

Sources: knowledge/nltk-expert/*.md (nltk.org API docs, VADER README).
"""
from __future__ import annotations

import re

import nltk
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder
from nltk.probability import FreqDist
from nltk.tokenize import TweetTokenizer

NLTK_VERSION = nltk.__version__

# VADER README "About the Scoring": standard compound thresholds.
POS_THRESHOLD = 0.05
NEG_THRESHOLD = -0.05

# Negations carry sentiment ("not worth"), so they are removed from the stopword set.
NEGATIONS = frozenset({
    "not", "no", "nor", "never", "don't", "doesn't", "didn't", "isn't", "wasn't", "weren't",
    "won't", "wouldn't", "can't", "cannot", "couldn't", "shouldn't", "aren't", "haven't",
    "hasn't", "hadn't", "ain't", "mustn't", "needn't", "don", "doesn", "didn", "isn", "wasn",
    "weren", "won", "wouldn", "couldn", "shouldn", "aren", "haven", "hasn", "hadn",
})
# Ecommerce noise words (docs/01-nltk.md).
DOMAIN_STOPWORDS = frozenset({
    "product", "item", "amazon", "bought", "buy", "ordered", "order", "one", "get", "would",
    "really", "also", "use", "used", "using", "got", "thing", "things", "will", "just", "even",
    "much", "make", "made", "could", "like", "lot", "bit", "stuff", "since", "still", "well",
    "first", "two", "way", "say", "think", "know", "go", "take",
})

# Beauty/ecommerce words missing from the VADER lexicon (checked against nltk 3.9.4's
# vader_lexicon). Valences on VADER's -4..+4 scale, set conservatively by the team.
# Applied with setdefault, so existing VADER ratings are never overridden. Shared by the
# build and the browser, so scores stay identical. Evaluated in docs/evaluation.md.
DOMAIN_LEXICON = {
    "flimsy": -1.8, "cheap": -0.8, "cheaply": -1.5, "greasy": -1.4, "sticky": -1.0, "leaky": -1.6,
    "leaking": -1.4, "leaks": -1.2, "flaky": -1.1, "smelly": -1.6, "overpriced": -1.9, "burning": -1.2,
    "streaky": -1.3, "clumpy": -1.3, "patchy": -1.2, "chipped": -1.1, "peeling": -1.0, "scratchy": -1.2,
    "frizzy": -1.0, "refund": -0.8,
    "soft": 1.2, "smooth": 1.2, "silky": 1.6, "shiny": 1.1, "sturdy": 1.4, "durable": 1.4,
    "lightweight": 0.8, "moisturizing": 1.2, "hydrating": 1.2, "nourishing": 1.3,
}
# Bare negations are kept for collocations ("not worth") but are not useful as single top terms.
NEGATION_TERMS = frozenset({"not", "no", "nor", "never"})

_RE_WORD = re.compile(r"^[a-z][a-z']*[a-z]$|^[a-z]$")

_tokenizer = TweetTokenizer(preserve_case=False, reduce_len=True)
_sia = None
_stopwords = None
_punkt = None


def stopword_set() -> frozenset:
    """NLTK English stopwords minus negations, plus ecommerce noise words."""
    global _stopwords
    if _stopwords is None:
        from nltk.corpus import stopwords
        _stopwords = frozenset((set(stopwords.words("english")) - NEGATIONS) | DOMAIN_STOPWORDS)
    return _stopwords


def sia():
    """One shared SentimentIntensityAnalyzer (constructing one per text is slow)."""
    global _sia
    if _sia is None:
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        _sia = SentimentIntensityAnalyzer()
        for word, valence in DOMAIN_LEXICON.items():
            _sia.lexicon.setdefault(word, valence)
    return _sia


def tokenize(text: str) -> list:
    """TweetTokenizer: lowercase (except emoticons), 'cooool' -> 'cool'-ish. No data needed."""
    return _tokenizer.tokenize(text or "")


def split_sentences(text: str) -> list:
    """Punkt sentence split (needs the punkt_tab English tables on nltk.data.path)."""
    global _punkt
    if _punkt is None:
        from nltk.tokenize.punkt import PunktTokenizer
        _punkt = PunktTokenizer("english")
    return [s.strip() for s in _punkt.tokenize((text or "").strip()) if s.strip()]


def label(compound: float) -> str:
    if compound >= POS_THRESHOLD:
        return "positive"
    if compound <= NEG_THRESHOLD:
        return "negative"
    return "neutral"


def vader(text: str) -> dict:
    """VADER on raw text. Stopwords are never removed before VADER (it uses negations, caps, '!')."""
    s = sia().polarity_scores(text or "")
    out = {k: round(float(s[k]), 4) for k in ("compound", "pos", "neu", "neg")}
    out["label"] = label(out["compound"])
    return out


def compound(text: str) -> float:
    return round(float(sia().polarity_scores(text or "")["compound"]), 4)


def words(tokens) -> list:
    """Lowercase alphabetic words (apostrophes allowed inside, e.g. "don't")."""
    return [t for t in (str(x).lower() for x in tokens) if _RE_WORD.match(t)]


def content_words(tokens) -> list:
    stop = stopword_set()
    return [w for w in words(tokens) if w not in stop and (len(w) > 2 or w == "no")]


def top_terms(docs, n: int = 20) -> list:
    """FreqDist over content words of many token lists (spaCy lemmas in the build).

    freq is relative to all content words; bare negations are counted but not listed.
    """
    fd = freq_table(docs)
    total = fd.N()
    for neg in NEGATION_TERMS:
        fd.pop(neg, None)
    if not total:
        return []
    items = sorted(fd.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
    return [{"term": t, "count": int(c), "freq": round(c / total, 4)} for t, c in items]


def freq_table(docs) -> FreqDist:
    fd = FreqDist()
    for doc in docs:
        fd.update(content_words(doc))
    return fd


def key_phrases(docs, n: int = 10, min_freq: int = 3) -> list:
    """Bigram collocations scored by likelihood ratio, with a frequency filter.

    Bigrams are built per document from adjacent words (from_documents), then any
    bigram containing a stopword (negations are NOT stopwords) is filtered out.
    """
    stop = stopword_set()
    seqs = [words(d) for d in docs]
    seqs = [s for s in seqs if len(s) >= 2]
    if not seqs:
        return []
    finder = BigramCollocationFinder.from_documents(seqs)
    finder.apply_freq_filter(min_freq)
    finder.apply_word_filter(lambda w: w in stop or len(w) < 2)
    scored = finder.score_ngrams(BigramAssocMeasures.likelihood_ratio)
    scored = sorted(scored, key=lambda kv: (-round(kv[1], 4), kv[0]))[:n]
    return [
        {"phrase": " ".join(ng), "count": int(finder.ngram_fd[ng]), "score": round(float(sc), 4)}
        for ng, sc in scored
    ]


MAX_CHARS = 5000


def analyze(text: str) -> dict:
    """Everything NLTK says about one text. Used by the browser playground."""
    text = (text or "")[:MAX_CHARS]
    tokens = tokenize(text)
    ws = words(tokens)
    sentences = []
    sentence_words = []  # collocations never cross a sentence boundary
    for i, s in enumerate(split_sentences(text)):
        sentence_words.append(words(tokenize(s)))
        if i < 50:
            c = compound(s)
            sentences.append({"text": s, "compound": c, "label": label(c)})
    min_freq = 2 if len(ws) >= 150 else 1
    return {
        "source": "nltk",
        "nltk_version": NLTK_VERSION,
        "n_chars": len(text),
        "n_tokens": len(tokens),
        "tokens": tokens[:300],
        "sentiment": vader(text),
        "sentences": sentences,
        "top_words": top_terms([ws], n=10),
        "key_phrases": {
            "measure": "likelihood_ratio",
            "min_freq": min_freq,
            "items": key_phrases(sentence_words, n=8, min_freq=min_freq),
        },
    }
