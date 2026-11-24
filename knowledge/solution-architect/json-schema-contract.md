# JSON Schema data contract

Sources:
- https://json-schema.org/learn/getting-started-step-by-step
- https://python-jsonschema.readthedocs.io/en/stable/validate/

## JSON Schema basics (getting-started guide)
- "`$schema`: specifies which draft of the JSON Schema standard the schema adheres to." Use `"https://json-schema.org/draft/2020-12/schema"`.
- "`$id`: sets a URI for the schema." For example, `"https://nlpfinal.local/schemas/products.schema.json"`. It only needs to be unique and doesn't have to resolve.
- `title` and `description` are annotations. `type`, `properties`, `required`, `items`, `minimum`/`exclusiveMinimum` and `enum` are validation keywords. The guide's example: `"price": {"type": "number", "exclusiveMinimum": 0}`.
- Add `"additionalProperties": false` to catch typos between the pipeline and the frontend.
- Validate in Python with `Draft202012Validator` (see `knowledge/qa-engineer/json-schema-validation.md`).

## Contract outline (to be written as `schemas/*.schema.json`)
| File | Shape (top level) |
|---|---|
| `summary.json` | `{generated_at, data_as_of, category, n_products, n_reviews, sentiment_mix{pos,neu,neg}, top_products[parent_asin], weights{...}, metric_kind:"proxy"}` |
| `products.json` | `[{parent_asin, title, store, price|null, rating_number, n_reviews, adj_rating, mean_compound, pct_negative, velocity, score, rank, flags[]}]` |
| `product/<parent_asin>.json` | `{parent_asin, aspects[{aspect, mentions, mean_compound, top_opinions[]}], entities{BRAND[],ORG[],MONEY[],DATE[]}, top_terms{positive[],negative[]}, collocations{positive[],negative[]}, monthly[{month, n, mean_compound}], examples{most_helpful_negative, most_helpful_positive}}` |
| `aspects.json` | category-level aspect leaderboard |
| `trends.json` | category monthly series and trending terms |
| `build_info.json` | `{commit_ref, context, versions{python,nltk,spacy,model,pandas}, sample{n_products,n_reviews}, timings{}}` |
Rules: floats rounded to 4 decimals; dates in ISO 8601 (`YYYY-MM` for months); `null` rather than NaN; every list sorted deterministically.
