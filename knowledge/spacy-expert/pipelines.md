# Processing pipelines

Sources:
- https://spacy.io/usage/processing-pipelines
- https://github.com/explosion/spaCy/blob/master/website/docs/usage/processing-pipelines.mdx

## Calling the pipeline
- "When you call `nlp` on a text, spaCy will **tokenize** it and then **call each component** on the `Doc`, in order."
- The tokenizer is special: it "isn't part of the regular pipeline" and doesn't appear in `nlp.pipe_names`.
- Inspect a pipeline with `nlp.pipeline` (`(name, component)` tuples), `nlp.pipe_names`, and `nlp.components` / `nlp.component_names` (which include disabled components).
- **Order matters.** "it matters if you add the `EntityRuler` before or after the statistical entity recognizer." See entity-ruler-and-matchers.md.

## Batch processing with `nlp.pipe` (required for the build)
- "When processing large volumes of text, the statistical models are usually more efficient if you let them work on batches of texts. spaCy's `nlp.pipe` method takes an iterable of texts and yields processed `Doc` objects."
- It **returns a generator**: `list(nlp.pipe(texts))[0]` works and `nlp.pipe(texts)[0]` raises an error.
- Disable what you don't need for a pass:
  ```python
  for doc in nlp.pipe(texts, disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"]):
      print([(ent.text, ent.label_) for ent in doc.ents])
  ```
- Carry IDs through with `as_tuples=True`: the input is `(text, context)` and the output is `(doc, context)`.
  ```python
  for doc, ctx in nlp.pipe(((r["text"], {"review_id": r["id"]}) for r in reviews), as_tuples=True):
      ...
  ```
- Multiprocessing: `nlp.pipe(texts, n_process=4)`, or `n_process=-1` for all CPUs ("use with caution!"). Starting processes adds overhead because "the model data is copied in memory for each new process". "it can be faster to use a smaller number of processes with a larger batch size."
- "Default batch size is `nlp.batch_size` (typically 1000)". Example: `nlp.pipe(texts, n_process=2, batch_size=2000)`.

## Disable vs. exclude
- `spacy.load("en_core_web_sm", disable=["parser"])` loads the component but disables it, and you can turn it back on with `nlp.enable_pipe("parser")`.
- `exclude=[...]` doesn't load the component at all. "As of v3.0, the `disable` keyword argument specifies components to load but disable ... specified separately using the new `exclude` keyword argument."
- `enable=[...]` disables everything else. Passing the same component to both `enable` and `disable` raises an error.
- To disable components temporarily: `with nlp.select_pipes(disable=["tagger","parser","lemmatizer"]): ...`, or keep the return value and call `.restore()` on it.

## Component dependencies (important when disabling)
- The `lemmatizer` in rule mode "requires `Token.pos` to be set by a previous component". It needs `tagger` and `attribute_ruler`, so don't disable them when you need lemmas.
- `Doc.noun_chunks` and `Doc.sents` (by default) need the `parser`.
- "If you don't need any of the syntactic information, you should disable the parser. Disabling the parser will make spaCy load and run much faster."

## Project defaults
- Load the pipeline once: `nlp = spacy.load("en_core_web_sm")`, then add `entity_ruler` before `ner`.
- Run a single pass, `nlp.pipe(texts, batch_size=256)`, with every component enabled, because we need lemmas, the parse, noun chunks and entities. Measure before trying `n_process=2` on the Netlify build machine.
- Truncate texts to about 2,000 characters before parsing.
