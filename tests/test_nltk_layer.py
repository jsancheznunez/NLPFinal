"""analyzer/nltk_layer.py: stopwords, VADER thresholds, FreqDist, collocations, Pyodide-safety."""
import ast
from pathlib import Path

import pytest

from analyzer import contract, nltk_layer as nl

LAYER = Path(nl.__file__)


def test_nltk_version_pinned():
    assert nl.NLTK_VERSION == "3.9.4"  # must equal Pyodide 314.0.8's nltk


def test_module_is_pyodide_safe():
    """stdlib + nltk + regex only, and no nltk.download() anywhere."""
    tree = ast.parse(LAYER.read_text(encoding="utf-8"))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    assert roots <= {"__future__", "re", "nltk", "regex", "json", "math", "collections"}, roots
    calls = [n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
    assert "download" not in calls


@pytest.mark.parametrize("word", ["not", "no", "never", "don't", "isn't", "wasn't", "nor"])
def test_stopwords_keep_negations(word):
    assert word not in nl.stopword_set()


@pytest.mark.parametrize("word", ["the", "and", "product", "amazon", "bought"])
def test_stopwords_drop_noise(word):
    assert word in nl.stopword_set()


@pytest.mark.parametrize("text,label", [
    ("I love this, it is amazing!", "positive"),
    ("This is not good.", "negative"),
    ("Terrible. It broke after one day.", "negative"),
    ("The box contains a bottle.", "neutral"),
    ("The strap is flimsy.", "negative"),   # domain lexicon addition
    ("VADER is smart, handsome, and funny.", "positive"),
])
def test_vader_labels(text, label):
    assert nl.vader(text)["label"] == label


@pytest.mark.parametrize("c,label", [(0.05, "positive"), (0.0499, "neutral"), (-0.0499, "neutral"), (-0.05, "negative")])
def test_thresholds(c, label):
    assert nl.label(c) == label


def test_vader_howto_example_unchanged():
    # NLTK sentiment HOWTO: "VADER is smart, handsome, and funny." -> compound 0.8316
    assert nl.vader("VADER is smart, handsome, and funny.")["compound"] == 0.8316


def test_domain_lexicon_never_overrides_vader():
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    base = SentimentIntensityAnalyzer().lexicon
    for w, v in nl.DOMAIN_LEXICON.items():
        assert nl.sia().lexicon[w] == base.get(w, v)


def test_tweet_tokenizer_lowercases_and_keeps_emoticons():
    assert nl.tokenize("Sooooo GOOD :-) don't") == ["sooo", "good", ":-)", "don't"]


def test_top_terms_excludes_stopwords_and_bare_negations():
    terms = nl.top_terms([["the", "strap", "be", "not", "strap", "great"], ["strap", "product"]], n=5)
    assert terms[0] == {"term": "strap", "count": 3, "freq": 0.6}
    assert {t["term"] for t in terms} <= {"strap", "great"}


def test_key_phrases_keep_negation_and_respect_freq_filter():
    docs = [["not", "worth", "the", "money"]] * 3 + [["battery", "life", "is", "great"]] * 3 + [["rare", "pair"]]
    phrases = nl.key_phrases(docs, n=10, min_freq=3)
    names = [p["phrase"] for p in phrases]
    assert "not worth" in names and "battery life" in names
    assert "rare pair" not in names                # below the frequency filter
    assert all("the" not in p.split() for p in names)  # stopword filter


def test_collocations_do_not_cross_sentences():
    r = nl.analyze("I paid the price. Not worth it. Not worth it.")
    assert "price not" not in [p["phrase"] for p in r["key_phrases"]["items"]]


def test_analyze_matches_schema():
    r = nl.analyze("The battery life is great!!! But the strap is not worth the price.")
    contract.validate("nltk_analysis", r)
    assert r["source"] == "nltk"
    assert len(r["sentences"]) == 2


def test_analyze_handles_empty_text():
    r = nl.analyze("")
    contract.validate("nltk_analysis", r)
    assert r["sentiment"]["label"] == "neutral" and r["n_tokens"] == 0
