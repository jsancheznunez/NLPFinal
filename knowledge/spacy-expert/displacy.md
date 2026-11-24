# displaCy: build-time visualizations for the static site

Sources:
- https://spacy.io/usage/visualizers
- https://spacy.io/api/top-level#displacy
- Source Markdown: github.com/explosion/spaCy/website/docs/usage/visualizers.mdx and api/top-level.mdx

## Rendering HTML without a server (what we use)
- "If you don't need the web server and just want to generate the markup – for example, to export it to a file or serve it in a custom way – you can use `displacy.render`... returns a string containing the markup."
  ```python
  from spacy import displacy
  html = displacy.render([doc1, doc2], style="dep", page=True)
  ```
- `page=True` wraps the markup in a full HTML page. `minify=True` gives compact markup. A `style="dep"` render returns SVG that can be written straight to a `.svg` file:
  ```python
  svg = displacy.render(doc, style="dep")
  Path("site/displacy/example-1.svg").write_text(svg, encoding="utf-8")
  ```
- **Don't** use `displacy.serve()`, which starts a web server. Netlify has no runtime Python.

## `displacy.render` arguments
| Arg | Meaning |
|---|---|
| `docs` | Doc(s), Span(s) or dicts |
| `style` | `"dep"` (default), `"ent"`, or `"span"` (spaCy 3.3+) |
| `page` | full HTML page (default `False`) |
| `minify` | minify HTML (default `False`) |
| `options` | visualizer-specific options (below) |
| `manual` | pass dicts instead of Docs (default `False`) |
| `jupyter` | force or disable notebook mode; auto-detected if `None` |

## Options
- **dep:** `compact` (square arrows, takes less space), `collapse_punct` (default `True`), `collapse_phrases` (merge noun phrases), `add_lemma` (show lemmas in a separate row), `fine_grained`, `color`, `bg`, `font` (default `"Arial"`), `distance` (default 175, or 150 in compact mode), `word_spacing`, `arrow_*`.
- **ent:** `ents` (which labels to show; `None` shows all), `colors` (label → color, e.g. `{"BRAND": "#7aecec"}`), `template`.

## Project usage
- At build time, pick about 6 representative review sentences (positive, negative, and mixed with "but"). Render a `dep` SVG with `{"compact": True, "add_lemma": True}` and an `ent` HTML page with `{"ents": ["BRAND","ORG","PRODUCT","MONEY","DATE"], "colors": {...}}`.
- Write them to `site/displacy/` and link them from the "How it works" page. Set colors that meet the frontend's contrast rules (see `knowledge/frontend-engineer/accessibility.md`).
