"""analyzer/metrics.py: formulas, weights, flags (synthetic table)."""
import math

import pandas as pd
import pytest

from analyzer import metrics as m

DAY = 86_400_000


def test_weights_sum_to_one():
    assert math.isclose(sum(m.WEIGHTS.values()), 1.0)


def test_bayesian_rating():
    assert m.bayesian_rating(0, 5.0, 4.0) == 4.0
    assert m.bayesian_rating(20, 5.0, 4.0) == 4.5
    assert m.bayesian_rating(1000, 5.0, 4.0) > 4.95


def test_zscore_constant_is_zero():
    assert (m.zscore(pd.Series([3.0, 3.0, 3.0])) == 0).all()


def test_r4_handles_nan():
    assert m.r4(float("nan")) is None and m.r4(1.23456) == 1.2346


def synthetic():
    rows = []
    end = 1_690_000_000_000
    # A: popular, negative; B: unpopular, very positive; C: trending (recent burst); D: average
    for i in range(30):
        rows.append(("AAAAAAAAAA", 2.0, end - i * 20 * DAY, -0.6))
    for i in range(30):
        rows.append(("BBBBBBBBBB", 5.0, end - i * 20 * DAY, 0.9))
    for i in range(12):
        rows.append(("CCCCCCCCCC", 4.0, end - i * 5 * DAY, 0.4))
    for i in range(30):
        rows.append(("DDDDDDDDDD", 4.0, end - i * 20 * DAY, 0.3))
    reviews = pd.DataFrame(rows, columns=["parent_asin", "rating", "timestamp", "compound"])
    reviews["helpful_vote"] = 0
    meta = pd.DataFrame({"parent_asin": ["AAAAAAAAAA", "BBBBBBBBBB", "CCCCCCCCCC", "DDDDDDDDDD"],
                         "rating_number": [50000, 15, 300, 900], "average_rating": [2.1, 4.9, 4.0, 4.0],
                         "price": [10.0, None, 30.0, 20.0]})
    return reviews, meta


def test_product_table_flags_and_ranks():
    reviews, meta = synthetic()
    t = m.product_table(reviews, meta, {"AAAAAAAAAA": {"top_negative_aspect": "strap", "neg_price_mentions": 4}})
    by = t.set_index("parent_asin")
    assert sorted(t["rank"]) == [1, 2, 3, 4]
    assert by.loc["AAAAAAAAAA", "best_seller_rank"] == 1
    assert "fix_top_complaint" in by.loc["AAAAAAAAAA", "flags"]
    assert "price_value_mismatch" in by.loc["AAAAAAAAAA", "flags"]
    assert "under_marketed_gem" in by.loc["BBBBBBBBBB", "flags"]
    assert "trending" in by.loc["CCCCCCCCCC", "flags"]
    assert by.loc["BBBBBBBBBB", "price_band"] == "unknown"
    assert any("strap" in r for r in by.loc["AAAAAAAAAA", "flag_reasons"])


def test_velocity_uses_data_as_of_not_today():
    reviews, meta = synthetic()
    t = m.product_table(reviews, meta)
    assert t.attrs["data_as_of"] == pd.to_datetime(reviews["timestamp"].max(), unit="ms", utc=True)


def test_month_range():
    assert m.month_range(pd.Timestamp("2023-09-04", tz="UTC"), 3) == ["2023-07", "2023-08", "2023-09"]
