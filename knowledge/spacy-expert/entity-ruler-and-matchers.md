# EntityRuler, PhraseMatcher, DependencyMatcher

Sources:
- https://spacy.io/usage/rule-based-matching
- https://spacy.io/api/entityruler
- Source Markdown: github.com/explosion/spaCy/website/docs/usage/rule-based-matching.mdx and api/entityruler.mdx

## EntityRuler
- "lets you add spans to the `Doc.ents` using token-based rules or exact phrase matches. It can be combined with the statistical `EntityRecognizer` to boost accuracy." Factory name: `"entity_ruler"`.
- Pattern formats:
  - Phrase pattern: `{"label": "ORG", "pattern": "Apple"}`
  - Token pattern: `{"label": "GPE", "pattern": [{"LOWER": "san"}, {"LOWER": "francisco"}]}`
  - An optional `"id"` groups variants of the same entity. The match's `ent.ent_id_` is set to that id.
- Overlap: "If any matches were to overlap, the pattern matching most tokens takes priority. If they also happen to be equally long, then the match occurring first in the `Doc` is chosen."
- **Placement:**
  - "If it's added **before the `"ner"` component**, the entity recognizer will respect the existing entity spans and adjust its predictions around it. This can significantly improve accuracy in some cases."
  - "If it's added **after the `"ner"` component**, the entity ruler will only add spans to the `doc.ents` if they don't overlap with existing entities predicted by the model. To overwrite overlapping entities, you can set `overwrite_ents=True`."
- Config keys: `phrase_matcher_attr` (e.g. `"LOWER"` for case-insensitive phrase patterns; default `None`), `validate` (default `False`), `overwrite_ents` (default `False`), `ent_id_sep` (default `"||"`).
- Pattern files: `ruler.to_disk("./patterns.jsonl")` and `nlp.add_pipe("entity_ruler").from_disk("./patterns.jsonl")`, one JSON pattern per line.
- Speed with many phrase patterns: `add_patterns` processes each phrase with `nlp`. Wrap it in `with nlp.select_pipes(enable="tagger"):`, or with nothing enabled when matching on LOWER/ORTH, to keep it fast.

### Project usage
```python
nlp = spacy.load("en_core_web_sm")
ruler = nlp.add_pipe("entity_ruler", before="ner", config={"phrase_matcher_attr": "LOWER"})
brands = sorted({s.strip() for s in meta["store"] if s and len(s.strip()) > 2})
with nlp.select_pipes(disable=nlp.pipe_names):   # phrase patterns only need the tokenizer
    ruler.add_patterns([{"label": "BRAND", "pattern": b, "id": b.lower()} for b in brands])
```
Save the patterns to `analyzer/patterns/brands.jsonl` so builds are reproducible.

## PhraseMatcher (issue phrases)
- `PhraseMatcher(nlp.vocab)` matches on the verbatim token text by default. Pass `attr="LOWER"` for case-insensitive matching.
- Build patterns with `nlp.make_doc(text)`, which runs only the tokenizer, not `nlp(text)`: `patterns = [nlp.make_doc(t) for t in TERMS]`, or `list(nlp.tokenizer.pipe(TERMS))`.
- `matcher.add("ISSUE_SHIPPING", patterns)`, then `for match_id, start, end in matcher(doc): span = doc[start:end]`.
- Project issue categories: shipping ("arrived damaged", "late delivery"), sizing ("runs small", "too big"), quality ("fell apart", "cheap material"), defect ("stopped working", "doesn't work").

## DependencyMatcher (optional alternative to hand-written loops)
- "lets you match patterns within the dependency parse using Semgrex operators. It requires a model containing a parser."
- Patterns are lists of dicts. The first dict defines the anchor with `RIGHT_ID` and `RIGHT_ATTRS`, and each later dict has `LEFT_ID`, `REL_OP`, `RIGHT_ID` and `RIGHT_ATTRS`. A name must be defined as a `RIGHT_ID` before it is used as a `LEFT_ID`.
- Operators: `A < B` (A is the immediate dependent of B), `A > B` (A is the immediate head of B), `A << B` / `A >> B` (chains), `A . B` (A immediately precedes B), `A ; B` (A precedes B), and others.
- Example aspect-opinion pattern, "the strap is flimsy":
  ```python
  [{"RIGHT_ID": "opinion", "RIGHT_ATTRS": {"DEP": "acomp", "POS": "ADJ"}},
   {"LEFT_ID": "opinion", "REL_OP": "<", "RIGHT_ID": "verb", "RIGHT_ATTRS": {"POS": {"IN": ["AUX", "VERB"]}}},
   {"LEFT_ID": "verb", "REL_OP": ">", "RIGHT_ID": "aspect", "RIGHT_ATTRS": {"DEP": {"IN": ["nsubj", "nsubjpass"]}}}]
  ```
