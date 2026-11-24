# Linguistic features used by the analyzer

Sources:
- https://spacy.io/usage/linguistic-features
- https://spacy.io/api/doc
- https://spacy.io/api/token
- Source Markdown: github.com/explosion/spaCy/website/docs/usage/linguistic-features.mdx

## Lemmatization
- "English pipelines include a rule-based lemmatizer":
  ```python
  nlp = spacy.load("en_core_web_sm")
  print(nlp.get_pipe("lemmatizer").mode)  # 'rule'
  print([t.lemma_ for t in nlp("I was reading the paper.")])
  # ['I', 'be', 'read', 'the', 'paper', '.']
  ```
- Since v3, "To have lemmas in a `Doc`, the pipeline needs to include a `Lemmatizer` component... The `"rule"` mode requires `Token.pos` to be set by a previous component." Trained pipelines already include the lookup tables they need.

## Dependency parse
- "spaCy uses the terms **head** and **child** to describe the words connected by a single arc ... **dep** is used for the arc label." Use `.dep_` for the string and `.dep` for the hash.
- The docs example for "Autonomous cars shift insurance liability toward manufacturers":

  | Text | Dep | Head |
  |---|---|---|
  | Autonomous | `amod` | cars |
  | cars | `nsubj` | shift |
  | shift | `ROOT` | shift |
  | insurance | `compound` | liability |
  | liability | `dobj` | shift |
  | toward | `prep` | shift |
  | manufacturers | `pobj` | toward |
- "every word has **exactly one head**... iterate over the arcs in the tree by iterating over the words in the sentence. This is usually the best way to match an arc of interest, from below." For example, find `amod` tokens and read `token.head`, instead of looping over every noun's children.
- Navigation: `token.children`, `token.lefts`/`token.rights` (in sentence order), `token.n_lefts`/`n_rights`, `token.subtree`, `token.ancestors`. Example: in "bright red apples on the tree", `doc[2].lefts` → `['bright', 'red']` and `doc[2].rights` → `['on']`.

## Noun chunks
- "Noun chunks are 'base noun phrases' – flat phrases that have a noun as their head... iterate over `Doc.noun_chunks`."
- `Doc.noun_chunks` yields `Span`s "if the document has been syntactically parsed". A base NP "does not permit other NPs to be nested within it – so no NP-level coordination, no prepositional phrases, and no relative clauses." It needs the parser.
- Each chunk has `chunk.text`, `chunk.root`, `chunk.root.dep_` and `chunk.root.head`. Docs example: "Autonomous cars" (root cars, nsubj → shift), "insurance liability" (root liability, dobj → shift), "manufacturers" (pobj → toward).
- Project normalization: drop leading `DET`/`PRON`/`NUM` tokens, lowercase, and use `chunk.root.lemma_` for grouping, e.g. "the batteries" → `battery`.

## Named entities
- "The standard way to access entity annotations is the `doc.ents` property, which produces a sequence of `Span` objects." Use `ent.label_`, `ent.start_char` and `ent.end_char`.
- Token-level access: `token.ent_iob_` (`B`, `I`, `O`) and `token.ent_type_`. Example: San → `B GPE`, Francisco → `I GPE`.
- `spacy.explain(label)` describes a label. The label set is listed in en-core-web-sm.md.

## Sentences
- `Doc.sents` "is only available when sentence boundaries have been set on the document by the `parser`, `senter`, `sentencizer`... It will raise an error otherwise." By default `en_core_web_sm` sets them with the parser (its `senter` is disabled).

## Aspect-opinion rules (project, built on the parse labels above)
| Pattern | Rule |
|---|---|
| "cheap zipper" | `tok.dep_ == "amod"` and `tok.head.pos_ in {"NOUN","PROPN"}` → (aspect `tok.head`, opinion `tok`) |
| "the strap is flimsy" | `tok.dep_ == "acomp"`; aspect = the `nsubj`/`nsubjpass` child of `tok.head` |
| "not great" | a `neg` child on the opinion or its head → negated |
| "soft and warm" | follow `conj` from the opinion to share the aspect |
| "hate the smell" | `dobj` of an opinion verb |
