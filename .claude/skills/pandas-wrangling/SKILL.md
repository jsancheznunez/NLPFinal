---
name: pandas-wrangling
description: "Join, group, aggregate and time-bucket review and product tables with pandas. Use for metrics, evaluation tables and sample statistics."
user-invocable: false
metadata:
  skill-id: S09
  shared-by: "data-engineer, metrics-engineer, eval-report-writer"
---

# pandas data wrangling & aggregation (S09)

Shared by: `data-engineer`, `metrics-engineer`, `eval-report-writer`. Matrix: `docs/expert-roster.md` §3.

- Left-join reviews to metadata on `parent_asin`. Some items lack metadata.
- Named aggregation: `df.groupby("parent_asin").agg(n=("rating","size"), mean=("rating","mean"))`.
- Time: `pd.to_datetime(df["timestamp"], unit="ms", utc=True)`, and monthly buckets with `pd.Grouper(key="ts", freq="MS")`.
- Export: `to_json(orient="records", date_format="iso")`. The epoch format is deprecated in pandas 3. Replace NaN with None before `json.dumps(..., allow_nan=False)`.
Details: `knowledge/metrics-engineer/pandas-aggregation.md`.
