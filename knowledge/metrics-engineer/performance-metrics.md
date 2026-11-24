# Project performance metrics (proxies)

Sources:
- docs/03-dataset.md (project decision)
- Dataset field definitions: https://amazon-reviews-2023.github.io/ (`rating_number` = "Number of ratings in the product", `average_rating` = "Rating of the product shown on the product page", `price` = "Price in US dollars (at time of crawling)")

| Metric | Definition | Fields |
|---|---|---|
| Popularity (best-seller proxy) | `rating_number` (catalogue-wide) and `n_reviews` (in the sample). Rank within the category | meta.rating_number, reviews |
| Adjusted rating | Bayesian average `(v*R + m*C)/(v+m)`: v = n ratings, R = product mean, C = category mean, m = 20 | rating |
| Sentiment | mean VADER `compound`; % negative (`compound <= -0.05`) | nltk-expert output |
| Review velocity | reviews in the last 6 months of data ÷ reviews in the 6 months before (add 1 to both to avoid dividing by zero) | timestamp |
| Aspect health | share of the product's aspect mentions with negative scores; its top 3 negative aspects | spacy-expert + nltk-expert output |
| Price band | quartiles of `price` within the category; `null` → "unknown" | meta.price |
| **Performance score** | z-score each signal within its category, then `0.35*popularity + 0.25*adj_rating + 0.25*sentiment + 0.15*velocity`. Show the weights in the UI and JSON | all |

## Opportunity flags (rules)
- **Fix the top complaint:** popularity in the top quartile, and sentiment or adjusted rating in the bottom quartile. Include its most frequent negative aspect.
- **Under-marketed gem:** sentiment in the top quartile and popularity in the bottom half.
- **Trending:** velocity ≥ 1.5 with at least 10 reviews in the recent window.
- **Price-value mismatch:** many negative MONEY-entity mentions (from spaCy) or "price"/"value" aspects with negative scores.

## Honesty rules
- Label popularity as a "sales proxy" in the JSON (`"metric_kind": "proxy"`) and in the UI.
- If a synthetic `sales.csv` is generated, add `"simulated": true` and a visible "Simulated data" badge. Never mix it into the performance score silently.
- Use the "data as of" date (the maximum timestamp in the sample), not today's date, as the reference point for velocity.
