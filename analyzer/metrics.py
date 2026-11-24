"""Metrics layer (pandas): best-seller proxies, performance score, trends, opportunity flags.

There are NO sales figures in Amazon Reviews 2023. Every "sales" number here is a
PROXY (rating_number = number of ratings on the product page, review counts and
review velocity) and is labelled metric_kind="proxy" in the JSON and the UI.
No simulated sales data is used.

Definitions: knowledge/metrics-engineer/performance-metrics.md.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

WEIGHTS = {"popularity": 0.35, "adj_rating": 0.25, "sentiment": 0.25, "velocity": 0.15}
WEIGHTS_NOTE = (
    "score = 0.35*z(log1p(rating_number)) + 0.25*z(Bayesian rating, m=20) "
    "+ 0.25*z(mean VADER compound) + 0.15*z(log review velocity); z-scores within the category. "
    "rating_number and review velocity are sales PROXIES, not sales."
)
BAYES_M = 20
WINDOW_MONTHS = 6
TRENDING_VELOCITY = 1.5
TRENDING_MIN_RECENT = 5  # in the sample (reviews are capped per product, so 10 in the full data ~ 5 here)


def r4(x):
    """Round to 4 decimals; NaN/inf -> None (JSON is written with allow_nan=False)."""
    if x is None:
        return None
    x = float(x)
    if math.isnan(x) or math.isinf(x):
        return None
    return round(x, 4)


def bayesian_rating(v, R, C, m: int = BAYES_M):
    """(v*R + m*C) / (v + m): shrinks products with few ratings toward the category mean C."""
    return (v * R + m * C) / (v + m)


def zscore(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    sd = s.std(ddof=0)
    if not sd or np.isnan(sd):
        return pd.Series(0.0, index=s.index)
    return (s - s.mean()) / sd


def add_time(reviews: pd.DataFrame) -> pd.DataFrame:
    df = reviews.copy()
    df["ts"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df["month"] = df["ts"].dt.strftime("%Y-%m")
    return df


def data_as_of(df: pd.DataFrame) -> pd.Timestamp:
    """Reference date = latest review in the sample (never today's date)."""
    return df["ts"].max()


def windows(as_of: pd.Timestamp, months: int = WINDOW_MONTHS):
    recent_start = as_of - pd.DateOffset(months=months)
    prev_start = recent_start - pd.DateOffset(months=months)
    return prev_start, recent_start


def velocity_table(df: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    prev_start, recent_start = windows(as_of)
    recent = df[df["ts"] > recent_start].groupby("parent_asin").size()
    prev = df[(df["ts"] > prev_start) & (df["ts"] <= recent_start)].groupby("parent_asin").size()
    out = pd.DataFrame(index=sorted(df["parent_asin"].unique()))
    out["recent_reviews"] = recent.reindex(out.index, fill_value=0).astype(int)
    out["previous_reviews"] = prev.reindex(out.index, fill_value=0).astype(int)
    out["velocity"] = (out["recent_reviews"] + 1) / (out["previous_reviews"] + 1)
    return out


def price_bands(price: pd.Series) -> pd.Series:
    pct = price.rank(pct=True, method="average")
    bands = pd.Series("unknown", index=price.index, dtype=object)
    known = price.notna()
    bands[known & (pct <= 0.25)] = "low"
    bands[known & (pct > 0.25) & (pct <= 0.5)] = "mid-low"
    bands[known & (pct > 0.5) & (pct <= 0.75)] = "mid-high"
    bands[known & (pct > 0.75)] = "high"
    return bands


def product_table(reviews: pd.DataFrame, meta: pd.DataFrame, aspect_signals: dict | None = None) -> pd.DataFrame:
    """One row per product with proxies, score, rank and opportunity flags.

    reviews: parent_asin, rating, timestamp, helpful_vote, compound
    meta:    parent_asin, rating_number, average_rating, price
    aspect_signals: {asin: {"top_negative_aspect": str|None, "neg_price_mentions": int}}
    """
    aspect_signals = aspect_signals or {}
    df = add_time(reviews)
    df["is_negative"] = df["compound"] <= -0.05
    as_of = data_as_of(df)
    per = df.groupby("parent_asin").agg(
        n_reviews=("rating", "size"),
        mean_rating=("rating", "mean"),
        mean_compound=("compound", "mean"),
        pct_negative=("is_negative", "mean"),
        helpful_votes=("helpful_vote", "sum"),
    )
    m = meta.set_index("parent_asin").reindex(per.index)
    per["rating_number"] = m["rating_number"]
    per["average_rating"] = m["average_rating"]
    per["price"] = m["price"]
    per = per.join(velocity_table(df, as_of))

    C = df["rating"].mean()
    per["adj_rating"] = bayesian_rating(per["n_reviews"], per["mean_rating"], C)
    popularity = np.log1p(per["rating_number"].fillna(per["n_reviews"]).astype(float))
    per["z_popularity"] = zscore(popularity)
    per["z_adj_rating"] = zscore(per["adj_rating"])
    per["z_sentiment"] = zscore(per["mean_compound"])
    per["z_velocity"] = zscore(np.log(per["velocity"]))
    per["score"] = (WEIGHTS["popularity"] * per["z_popularity"] + WEIGHTS["adj_rating"] * per["z_adj_rating"]
                    + WEIGHTS["sentiment"] * per["z_sentiment"] + WEIGHTS["velocity"] * per["z_velocity"])
    per["score"] = per["score"].round(4)

    per = per.reset_index().rename(columns={"index": "parent_asin"})
    per = per.sort_values(["score", "parent_asin"], ascending=[False, True]).reset_index(drop=True)
    per["rank"] = np.arange(1, len(per) + 1)
    pop = popularity.reindex(per["parent_asin"]).to_numpy()
    asins = per["parent_asin"].tolist()
    order = sorted(range(len(per)), key=lambda i: (-pop[i], asins[i]))
    bsr = np.empty(len(per), dtype=int)
    for r, i in enumerate(order):
        bsr[i] = r + 1
    per["best_seller_rank"] = bsr  # best-seller PROXY rank (by rating_number)
    per["price_band"] = price_bands(per["price"])

    pop_pct = per["z_popularity"].rank(pct=True)
    sent_pct = per["z_sentiment"].rank(pct=True)
    adj_pct = per["z_adj_rating"].rank(pct=True)
    flags, reasons = [], []
    for i, row in per.iterrows():
        f, why = [], []
        sig = aspect_signals.get(row["parent_asin"], {})
        if pop_pct[i] >= 0.75 and (sent_pct[i] <= 0.25 or adj_pct[i] <= 0.25):
            f.append("fix_top_complaint")
            asp = sig.get("top_negative_aspect")
            why.append("Popular (top 25% by ratings) but bottom 25% on sentiment or adjusted rating"
                       + (f"; most negative aspect: '{asp}'" if asp else ""))
        if sent_pct[i] >= 0.75 and pop_pct[i] < 0.5:
            f.append("under_marketed_gem")
            why.append("Top 25% sentiment but below-median popularity proxy")
        if row["velocity"] >= TRENDING_VELOCITY and row["recent_reviews"] >= TRENDING_MIN_RECENT:
            f.append("trending")
            why.append(f"Review velocity {row['velocity']:.2f}x over the last {WINDOW_MONTHS} months "
                       f"({int(row['recent_reviews'])} recent reviews in the sample)")
        if sig.get("neg_price_mentions", 0) >= 3:
            f.append("price_value_mismatch")
            why.append(f"{sig['neg_price_mentions']} negative price/value mentions (spaCy aspects/MONEY, VADER-scored)")
        flags.append(f)
        reasons.append(why)
    per["flags"] = flags
    per["flag_reasons"] = reasons
    per.attrs["data_as_of"] = as_of
    return per


def monthly_ratings(df: pd.DataFrame, months: list) -> list:
    g = df.groupby("month").agg(n=("rating", "size"), mean_rating=("rating", "mean"))
    return [{"month": mo, "n_reviews": int(g["n"].get(mo, 0)),
             "mean_rating": r4(g["mean_rating"].get(mo)) if mo in g.index else None} for mo in months]


def monthly_sentiment(df: pd.DataFrame, months: list, with_neg: bool = False) -> list:
    d = df.assign(is_negative=df["compound"] <= -0.05)
    g = d.groupby("month").agg(n=("compound", "size"), mc=("compound", "mean"), neg=("is_negative", "mean"))
    out = []
    for mo in months:
        has = mo in g.index
        row = {"month": mo, "n_reviews": int(g["n"].get(mo, 0)),
               "mean_compound": r4(g["mc"].get(mo)) if has else None}
        if with_neg:
            row["pct_negative"] = r4(g["neg"].get(mo)) if has else None
        out.append(row)
    return out


def month_range(as_of: pd.Timestamp, n: int) -> list:
    end = pd.Period(as_of.strftime("%Y-%m"), freq="M")
    return [str(end - k) for k in range(n - 1, -1, -1)]
