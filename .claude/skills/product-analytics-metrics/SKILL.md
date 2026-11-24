---
name: product-analytics-metrics
description: "Definitions of best-seller proxies, Bayesian-adjusted rating, review velocity, the weighted performance score and opportunity flags. Use when computing, displaying or explaining product performance."
user-invocable: false
metadata:
  skill-id: S17
  shared-by: "solution-architect, metrics-engineer, frontend-engineer"
---

# Product analytics metrics (S17)

Shared by: `solution-architect`, `metrics-engineer`, `frontend-engineer`. Matrix: `docs/expert-roster.md` §3.

- No real sales data exists. Popularity = `rating_number` and sample review count, **labeled as a proxy**.
- Adjusted rating `(v*R + m*C)/(v+m)` with m = 20 and C = category mean.
- Velocity = reviews in the last 6 months ÷ the previous 6 months (+1 smoothing), measured relative to the dataset's "as of" date.
- Performance score = within-category z-scores weighted 0.35 popularity, 0.25 adjusted rating, 0.25 sentiment, 0.15 velocity. **Show the weights in the UI.**
- Flags: "Fix the top complaint", "Under-marketed gem", "Trending", "Price-value mismatch" (rules in `knowledge/metrics-engineer/performance-metrics.md`).
- Any simulated sales data carries `"simulated": true` and a visible badge, and is never mixed into the score.
