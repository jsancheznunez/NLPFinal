# pandas for product metrics

Sources:
- https://pandas.pydata.org/docs/user_guide/groupby.html
- https://pandas.pydata.org/docs/user_guide/timeseries.html
- https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html
- https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_json.html

The pinned pandas version must support Python 3.12. pandas 3.x requires Python >= 3.11.

## groupby and named aggregation
- `df.groupby(["A","B"]).agg("sum")`. The group keys become the index. `as_index=False` or `.reset_index()` keeps them as columns.
- **Named aggregation**: "The keywords are the *output* column names. The values are tuples whose first element is the column to select and the second element is the aggregation to apply":
  ```python
  per_product = reviews.groupby("parent_asin").agg(
      n_reviews=("rating", "size"),
      mean_rating=("rating", "mean"),
      mean_compound=("compound", "mean"),
      pct_negative=("is_negative", "mean"),
      helpful_votes=("helpful_vote", "sum"),
  )
  ```
  "additional keyword arguments are not passed through to the aggregation functions". Use `functools.partial` if a function needs extra arguments.
- `transform` returns a result with the same shape as the input, e.g. a per-category mean on every row: `df["cat_mean"] = df.groupby("category")["rating"].transform("mean")`.

## Time
- `pd.to_datetime(df["timestamp"], unit="ms", utc=True)`: "with `unit='ms'` and `origin='unix'`, the input values are treated as milliseconds". `utc=True` "always returns a timezone-aware UTC-localized" result.
- Monthly buckets: `df.set_index("ts").groupby("parent_asin").resample("MS").size()`, or `df.groupby(["parent_asin", pd.Grouper(key="ts", freq="MS")])`. `"MS"` is month start and `"ME"` is month end, as in the pandas offset-alias table.

## Exporting to JSON
- `DataFrame.to_json`: "NaN's and None will be converted to null and datetime objects will be converted to UNIX timestamps."
- `orient="records"` gives a list of row objects, the easiest shape for the frontend.
- `date_format`: "'epoch' date format is **deprecated** [since 3.0] and will be removed... please use 'iso'". **Always pass `date_format="iso"`.**
- `double_precision` defaults to 10. Use 4 for scores to keep the files small.
- Alternatively, build plain dicts and write them with `json.dumps(..., allow_nan=False)` (see data-engineer's notes) after `df.where(pd.notna(df), None)`.
