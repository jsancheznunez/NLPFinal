# 02 — What spaCy Does Best for the Ecommerce Product Performance Analyzer

**Role in the app:** spaCy handles the **linguistic structure layer**. It uses trained statistical models to find **named entities**, **noun chunks** (product features and aspects), **POS-aware lemmas**, and **dependency parses**. The parse links opinion words to the thing they describe ("the *strap* is *flimsy*"). This lets the analyzer go from "this product has a mean sentiment of 0.31" to "**customers like the color but complain about the strap**". This is called **aspect-based sentiment**, and it is the most impressive output of the project.

> **Deployment constraint:** spaCy is **not** in Pyodide's built-in package list. It depends on compiled Cython/C packages: `thinc`, `blis`, `cymem`, `preshed`, `murmurhash`, `srsly`. So spaCy should run **at build time on Netlify**, or offline, and not in the browser. See [04-netlify-deployment.md](04-netlify-deployment.md).

---

## 0. Model choice

| Model | Size (approx.) | Notes |
|---|---|---|
| `en_core_web_sm` | ~12 MB | **Recommended.** Fast on CPU and includes tagger, parser, NER and lemmatizer. Fine for a build-time batch job. |
| `en_core_web_md` | ~40 MB | Adds word vectors (`token.similarity`), useful for clustering aspect terms ("cost" ≈ "price"). |
| `en_core_web_lg` / `_trf` | 400 MB+ / transformer | Too slow and too large for a Netlify build. Avoid. |

Pin the model as a wheel in `requirements.txt` so builds are reproducible, using the GitHub release URL from spaCy's model docs. **Don't** run `python -m spacy download` during the build.

```python
import spacy
nlp = spacy.load("en_core_web_sm")
# Batch processing is essential for speed:
for doc in nlp.pipe(review_texts, batch_size=256, n_process=1):
    ...
# If you don't need NER for a pass, disable it:  nlp.pipe(texts, disable=["ner"])
```

## 1. Named Entity Recognition (NER)

`doc.ents` with labels such as `ORG`, `PRODUCT`, `GPE`, `MONEY`, `DATE`, `CARDINAL`, `PERSON`, `NORP`.

**Uses in the analyzer:**
- **Brand and competitor mentions** (`ORG`, `PRODUCT`): "Better than my old **Dyson**", "returned it and bought the **Shark**". Count competitor mentions per product. This becomes a "Competitive landscape" panel.
- **Price and value talk** (`MONEY`): "not worth **$40**" ties sentiment to price points. Join with the product `price` field from the metadata.
- **Durability and timing** (`DATE`): "broke after **two weeks**", "still going after **3 years**". This gives a product-lifespan signal.
- **Geography** (`GPE`): shipping and origin complaints ("shipped from **China**").

**Improve NER with an `EntityRuler`.** The small model often misses brand names. Add a rule-based `entity_ruler` *before* `ner`, filled with brand names from the metadata `store` field and product `title`s:

```python
ruler = nlp.add_pipe("entity_ruler", before="ner")
ruler.add_patterns([{"label": "BRAND", "pattern": s} for s in set(meta["store"]) if s])
```

## 2. Noun chunks → product aspects

`doc.noun_chunks` gives base noun phrases: "the battery life", "a cheap plastic clasp", "customer service".

**Uses:**
- **Aspect extraction.** Normalize each chunk: lowercase it, drop determiners and pronouns (`token.pos_ in {"DET","PRON"}`), and take the lemma of the root ("the batteries" → "battery"). Count the result per product and category. The most common chunks are the product's **aspects**, and they're usually more readable than unigrams.
- **Category-level aspect lists.** "What do people talk about for Beauty products?" might give scent, skin, packaging, price.
- Cross-check them with NLTK collocations. Phrases found by both methods are strong aspects.

## 3. Lemmatization

`token.lemma_` uses POS context, so "running shoes" keeps the noun "running" while "was running" → "run", and "batteries" → "battery". This is better than NLTK's WordNet lemmatizer, which assumes everything is a noun unless told otherwise.

**Hybrid pattern (the main point of NLTK + spaCy integration):** use spaCy for tokens and lemmas with `token.is_stop`, `token.is_punct` and `token.like_num` filters. Then pass the lemma list to **NLTK's `FreqDist` and `BigramCollocationFinder`**. That gives cleaner frequency and collocation output than either library would alone.

## 4. Dependency parsing → aspect-based sentiment

The dependency parse (`token.dep_`, `token.head`, `token.children`) shows **which adjective describes which noun**. The rules below cover most review sentences:

| Pattern | Example | Rule |
|---|---|---|
| Adjectival modifier | "**cheap** *zipper*" | `tok.dep_ == "amod"` → (aspect = `tok.head`, opinion = `tok`) |
| Predicative adjective | "the *strap* is **flimsy**" | `tok.dep_ == "acomp"` with a `nsubj` sibling → (aspect = subject, opinion = `tok`) |
| Negation | "the fit is **not** great" | a `neg` child on the opinion word or its head flips polarity |
| Conjunction | "*soft* and **warm**" | follow `conj` to share the aspect |
| Verb-object complaint | "**hate** the *smell*" | `dobj` of an opinion verb |

```python
def aspect_opinions(doc):
    pairs = []
    for tok in doc:
        if tok.dep_ == "amod" and tok.head.pos_ in {"NOUN", "PROPN"}:
            pairs.append((tok.head, tok))
        elif tok.dep_ == "acomp":
            subj = [c for c in tok.head.children if c.dep_ in {"nsubj", "nsubjpass"}]
            if subj:
                pairs.append((subj[0], tok))
    out = []
    for aspect, opinion in pairs:
        negated = any(c.dep_ == "neg" for c in list(opinion.children) + list(opinion.head.children))
        out.append((aspect.lemma_.lower(), opinion.lemma_.lower(), negated))
    return out
```

**Score each pair with NLTK's VADER.** Pass `"not " + opinion` when the pair is negated, or score the whole sentence span. Then aggregate per (product, aspect): number of mentions and mean sentiment. That produces output like:

> **Product B0XYZ — aspects**: color (+0.62, 140 mentions), size (−0.18, 96), strap (−0.55, 41) → *Opportunity: fix the strap*.

spaCy's `Matcher` and `DependencyMatcher` can express these rules declaratively if the team prefers patterns over Python loops.

## 5. Other spaCy features worth using

| Feature | Use |
|---|---|
| `doc.sents` | Sentence segmentation based on the parse. Use it as the unit for per-sentence VADER scoring if you want one segmentation for everything. |
| `token.pos_` / `token.tag_` | Filter adjectives (opinion words) and nouns (aspects). Count the top adjectives per product. |
| `Matcher` / `PhraseMatcher` | Fast detection of fixed issue phrases: "arrived damaged", "stopped working", "runs small", "smells like". Use them to tag **issue categories** (shipping, quality, sizing, defect). |
| `displacy.render(doc, style="dep"/"ent")` | Make static SVG/HTML visualizations of parses and entities **at build time** and embed them in the site. This is a nice "how it works" demo page that doesn't need spaCy in the browser. |
| `token.similarity` (md model) | Cluster near-synonymous aspects. |
| `Doc.to_json()` / `DocBin` | Serialize processed docs so later pipeline steps don't re-parse. |

## 6. Performance budget (important for the Netlify build)

- Keep the build corpus **sampled** (e.g. 10–50k reviews). Run `nlp.pipe(..., batch_size=256)` with only the components you need.
- Cache the processed results. You can commit the generated JSON to the repo, or rely on Netlify's build cache, so each deploy doesn't re-run the whole pipeline. See [04-netlify-deployment.md](04-netlify-deployment.md).
- Truncate very long reviews (e.g. the first 2,000 characters). Parse time grows with length, and the main opinion is usually near the start.

## Sources
- spaCy usage docs: https://spacy.io/usage/linguistic-features (NER, noun chunks, dependency parse, lemmatization), https://spacy.io/usage/rule-based-matching (EntityRuler, Matcher, DependencyMatcher), https://spacy.io/models/en
- spaCy in the browser is not supported out of the box: Pyodide's package list has no `spacy`/`thinc`/`blis` (https://pyodide.org/en/stable/usage/packages-in-pyodide.html). The open request is https://github.com/pyodide/pyodide-recipes/issues/179 (opened 2020, still open). Community experiment: https://spacy.io/universe/project/spacy-wasm (SyedAhkam/spacy-wasm, with custom-built wheels; not maintained by spaCy or Pyodide).
