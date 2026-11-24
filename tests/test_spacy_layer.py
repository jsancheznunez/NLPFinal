"""analyzer/spacy_layer.py: aspect-opinion rules, EntityRuler BRAND/PRODUCT, noun chunks."""
import pytest

from analyzer import spacy_layer as sl


def pairs(nlp, text):
    return [(p["aspect"], p["opinion"], p["negated"]) for s in sl.extract(nlp(text))["sentences"] for p in s["pairs"]]


def test_entity_ruler_before_ner(nlp):
    names = nlp.pipe_names
    assert names.index("entity_ruler") < names.index("ner")


@pytest.mark.parametrize("text,expected", [
    ("The strap is flimsy.", ("strap", "flimsy", False)),                 # acomp + nsubj
    ("It has a cheap zipper.", ("zipper", "cheap", False)),               # amod
    ("The battery life is not great.", ("battery life", "great", True)),  # compound aspect + neg
    ("I hate the smell.", ("smell", "hate", False)),                      # opinion verb + dobj
])
def test_aspect_rules(nlp, text, expected):
    assert expected in pairs(nlp, text)


def test_conj_shares_aspect(nlp):
    got = pairs(nlp, "The brush is soft and gentle.")
    assert ("brush", "soft", False) in got and ("brush", "gentle", False) in got


def test_non_opinion_adjectives_ignored(nlp):
    assert pairs(nlp, "The other bottle was the same size.") == []


def test_brand_entity_from_store(nlp):
    ents = sl.extract(nlp("I switched to Olaplex last month and PURE BODY NATURALS salt."))["entities"]
    assert ("Olaplex", "BRAND") in ents
    assert ("Pure Body Naturals", "BRAND") in ents  # canonical store name via pattern id


def test_common_word_store_not_a_brand(nlp):
    ents = sl.extract(nlp("Okay, this works."))["entities"]
    assert all(label != "BRAND" for _, label in ents)


def test_noun_chunks_normalized(nlp):
    chunks = sl.extract(nlp("The batteries died and the cheap zipper broke."))["noun_chunks"]
    assert "battery" in chunks and "zipper" in chunks


def test_lemmas_are_lowercase_alpha(nlp):
    f = sl.extract(nlp("I was reading the reviews. It doesn't work!"))
    lemmas = [l for s in f["sentences"] for l in s["lemmas"]]
    assert "read" in lemmas and "review" in lemmas and "not" in lemmas
    assert all(l.isalpha() and l == l.lower() for l in lemmas)


def test_displacy_files(nlp, tmp_path):
    files = sl.render_displacy(nlp, ["The strap is flimsy.", "Great color, but the cap broke."], tmp_path)
    assert files == ["dep-1.svg", "dep-2.svg", "entities.html"]
    assert (tmp_path / "dep-1.svg").read_text().lstrip().startswith("<svg")
