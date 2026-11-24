"""spaCy layer: NER (+ BRAND/PRODUCT EntityRuler), noun chunks, lemmas,
dependency-based aspect-opinion pairs, and pre-rendered displaCy files.

Runs ONLY in the Netlify Python build (spaCy cannot run in Pyodide).
Model: en_core_web_sm 3.8.0 with spacy>=3.8.0,<3.9.0.

This module is pure spaCy. Sentiment scores for the aspect-opinion pairs are
added by the build with NLTK VADER (analyzer.nltk_layer), so the UI labels them
"spaCy + NLTK".

Sources: knowledge/spacy-expert/*.md (spacy.io usage + API docs).
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import spacy
from spacy import displacy

MODEL = "en_core_web_sm"
MAX_CHARS = 2000

# Entity labels kept in the outputs (CARDINAL/ORDINAL are mostly noise in reviews).
KEEP_LABELS = frozenset({"BRAND", "PRODUCT", "ORG", "PERSON", "GPE", "NORP", "MONEY", "DATE",
                         "TIME", "QUANTITY", "PERCENT", "EVENT", "WORK_OF_ART", "FAC", "LOC"})
# Aspect heads that say nothing about a specific product attribute.
GENERIC_ASPECTS = frozenset({
    "product", "item", "thing", "one", "stuff", "lot", "bit", "time", "way", "amazon", "review",
    "star", "stars", "order", "purchase", "buy", "money", "day", "week", "month", "year", "kind",
    "part", "deal", "job", "people", "everyone", "anyone", "someone", "nothing", "something",
    "anything", "everything", "lol", "i", "it", "me", "you", "she", "he", "they", "we", "use",
})
OPINION_VERBS = frozenset({"love", "hate", "like", "dislike", "adore", "enjoy", "recommend", "regret"})
# Adjectives that are not opinions ("only", "same", "other", "rechargeable") in amod/acomp slots.
NON_OPINION_ADJ = frozenset({
    "only", "same", "other", "own", "many", "few", "more", "most", "much", "several", "such", "last",
    "first", "next", "new", "old", "whole", "entire", "different", "certain", "various", "real", "sure",
    "able", "full", "single", "double", "extra", "regular", "original", "previous", "actual", "total",
    "overall", "main", "second", "third", "electric", "rechargeable", "manual", "daily", "dry", "wet",
    "oily", "curly", "straight", "thick", "thin", "fine", "long", "short", "dark", "light", "black",
    "white", "red", "pink", "blue", "green", "brown", "blonde", "gray", "grey", "purple", "yellow",
    "natural", "sensitive", "facial", "free", "available", "similar", "specific", "less", "least",
    "top", "bottom", "front", "back", "left", "right", "half", "cold", "hot", "warm", "little",
})
STORE_BLOCKLIST = frozenset({"generic", "unknown", "n/a", "na", "none", "amazon", "various", "other"})

DISPLACY_ENT_COLORS = {  # light backgrounds, dark label text: > 4.5:1 contrast with #111
    "BRAND": "#c7f0f0", "PRODUCT": "#fde2b8", "ORG": "#dcd3fa", "MONEY": "#d4f5c9",
    "DATE": "#f9d4e0", "QUANTITY": "#e6e6e6", "PERSON": "#fff3b0", "GPE": "#cfe3ff",
}


# --------------------------------------------------------------------------- patterns
def _variants(phrase: str) -> list:
    out = {phrase, phrase.title(), phrase.upper()}
    return sorted(v for v in out if v.strip())


def build_patterns(metas, common_words=frozenset()) -> list:
    """EntityRuler phrase patterns from metadata: `store` -> BRAND, short title head -> PRODUCT.

    The ruler matches on ORTH (case-sensitive) with a few case variants, so a
    store named e.g. "Lovely" does not tag every lowercase "lovely". Single-word stores
    that are common words (``common_words``, e.g. "Okay") are skipped. The pattern ``id``
    is the canonical store/title text, so "OZ Naturals" and "Oz Naturals" count as one.
    """
    brands, products = {}, {}
    for m in metas:
        store = (m.get("store") or "").strip()
        single_common = " " not in store and store.lower() in common_words
        if len(store) > 2 and store.lower() not in STORE_BLOCKLIST and not single_common:
            brands[store.lower()] = store
        title = (m.get("title") or "").strip()
        head = re.split(r"[,(|\-–:/]", title, maxsplit=1)[0].strip()
        if store and head.lower().startswith(store.lower()):
            head = head[len(store):].strip()
        toks = head.split()
        if 2 <= len(toks) <= 4 and len(head) <= 40 and not all(t.lower() in common_words for t in toks):
            products[head.lower()] = head
    patterns = []
    for key in sorted(brands):
        for v in _variants(brands[key]):
            patterns.append({"label": "BRAND", "pattern": v, "id": brands[key]})
    for key in sorted(products):
        for v in _variants(products[key]):
            patterns.append({"label": "PRODUCT", "pattern": v, "id": products[key]})
    return patterns


def load_nlp(patterns=None):
    """en_core_web_sm + an EntityRuler placed before "ner" (the NER respects its spans)."""
    nlp = spacy.load(MODEL)
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    if patterns:
        with nlp.select_pipes(disable=nlp.pipe_names):  # phrase patterns only need the tokenizer
            ruler.add_patterns(patterns)
    return nlp


def model_version(nlp) -> str:
    return f"{nlp.meta.get('name', 'core_web_sm')}-{nlp.meta.get('version', '?')}"


# --------------------------------------------------------------------------- features
def _aspect_text(tok):
    """'battery life' from the head noun plus its compound modifiers; lemma for the head."""
    if tok.pos_ not in ("NOUN", "PROPN"):
        return None
    head = tok.lemma_.lower()
    if head in GENERIC_ASPECTS or not head.isalpha() or len(head) < 3:
        return None
    mods = [c.lower_ for c in tok.lefts if c.dep_ == "compound" and c.pos_ in ("NOUN", "PROPN") and c.is_alpha]
    return " ".join(mods + [head])


def _negated(*toks) -> bool:
    return any(c.dep_ == "neg" for t in toks if t is not None for c in t.children)


def _with_conj(op):
    """'soft and warm': follow conj links from the opinion so both share the aspect."""
    out = [op]
    for c in op.children:
        if c.dep_ == "conj" and c.pos_ == "ADJ":
            out.append(c)
    return out


def aspect_pairs(sent) -> list:
    """(aspect, opinion, negated) triples from dependency rules (docs/02-spacy.md)."""
    found = []
    for tok in sent:
        # 1) "cheap zipper": amod ADJ -> head noun
        if tok.dep_ == "amod" and tok.pos_ == "ADJ":
            asp = _aspect_text(tok.head)
            if asp:
                found.append((asp, tok, _negated(tok)))
        # 2) "the strap is flimsy": acomp ADJ, aspect = nsubj of the verb
        elif tok.dep_ == "acomp" and tok.pos_ == "ADJ":
            verb = tok.head
            for subj in (c for c in verb.children if c.dep_ in ("nsubj", "nsubjpass")):
                asp = _aspect_text(subj)
                if asp:
                    for op in _with_conj(tok):
                        found.append((asp, op, _negated(tok, verb)))
        # 3) "hate the smell": opinion verb + direct object
        elif tok.dep_ == "dobj" and tok.head.lemma_.lower() in OPINION_VERBS:
            asp = _aspect_text(tok)
            if asp:
                found.append((asp, tok.head, _negated(tok.head)))
    pairs, seen = [], set()
    for asp, op, neg in found:
        opinion = op.lemma_.lower() if op.pos_ == "VERB" else op.lower_
        key = (asp, opinion, neg)
        if key not in seen and opinion.isalpha() and opinion not in NON_OPINION_ADJ:
            seen.add(key)
            pairs.append({"aspect": asp, "opinion": opinion, "negated": bool(neg)})
    return pairs


def _chunk_text(chunk):
    toks = list(chunk)
    while toks and toks[0].pos_ in ("DET", "PRON", "NUM", "PUNCT", "SYM"):
        toks = toks[1:]
    root = chunk.root
    if not toks or root.pos_ not in ("NOUN", "PROPN") or root.i not in {t.i for t in toks}:
        return None
    if root.lemma_.lower() in GENERIC_ASPECTS:
        return None
    # Keep the noun core ("battery life"), drop adjectives ("cheap") that are opinions.
    parts = [t.lower_ for t in toks
             if t.i != root.i and t.is_alpha and t.pos_ in ("NOUN", "PROPN")] + [root.lemma_.lower()]
    text = " ".join(parts)
    return text if len(text) >= 3 and root.lemma_.isalpha() else None


def extract(doc) -> dict:
    """Features of one review Doc (plain Python types only)."""
    sentences = []
    for sent in doc.sents:
        lemmas = [t.lemma_.lower() for t in sent if t.lemma_.isalpha()]
        sentences.append({"text": sent.text.strip(), "lemmas": lemmas, "pairs": aspect_pairs(sent)})
    ents = [((e.ent_id_ if e.label_ in ("BRAND", "PRODUCT") and e.ent_id_ else e.text.strip()), e.label_)
            for e in doc.ents if e.label_ in KEEP_LABELS and e.text.strip()]
    chunks = [c for c in (_chunk_text(ch) for ch in doc.noun_chunks) if c]
    return {"sentences": sentences, "entities": ents, "noun_chunks": chunks}


def process(nlp, texts, batch_size: int = 256) -> list:
    """One nlp.pipe pass with every component enabled (lemmas, parse, chunks, NER)."""
    clipped = ((t or "")[:MAX_CHARS] for t in texts)
    return [extract(doc) for doc in nlp.pipe(clipped, batch_size=batch_size)]


def count_items(values, n: int) -> list:
    c = Counter(values)
    return [{"text": t, "count": k} for t, k in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:n]]


def count_entities(pairs, n: int) -> list:
    c = Counter(pairs)
    return [{"text": t, "label": l, "count": k}
            for (t, l), k in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:n]]


# --------------------------------------------------------------------------- displaCy
def render_displacy(nlp, sentences, out_dir: Path) -> list:
    """Write dep-<i>.svg per sentence and one entities.html page (no server: displacy.render)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    docs = list(nlp.pipe(sentences))
    for i, doc in enumerate(docs, start=1):
        svg = displacy.render(doc, style="dep", options={"compact": True, "add_lemma": True})
        # displaCy puts a random uuid4 hex in the SVG ids; make it stable so builds are byte-identical.
        svg = re.sub(r"[0-9a-f]{32}(?=-\d)", f"displacy-dep-{i}", svg)
        path = out_dir / f"dep-{i}.svg"
        path.write_text(svg, encoding="utf-8")
        written.append(path.name)
    ent_html = displacy.render(
        docs, style="ent", page=True,
        options={"ents": sorted(DISPLACY_ENT_COLORS), "colors": DISPLACY_ENT_COLORS})
    (out_dir / "entities.html").write_text(ent_html, encoding="utf-8")
    written.append("entities.html")
    return written
