"""Sample Amazon Reviews 2023 (McAuley Lab) into a small, committed dataset.

Run locally, ONCE. Never on Netlify (the build only reads data/sample/).

    python scripts/prepare_data.py                 # All_Beauty sample + fixtures (default)
    python scripts/prepare_data.py --category Grocery_and_Gourmet_Food --skip-fixtures   # current sample
    python scripts/prepare_data.py --skip-fixtures

The raw .jsonl.gz files are streamed from mcauleylab.ucsd.edu into a gitignored
cache (data/raw/) and then read twice with gzip.open(..., "rt"):
  pass 1 counts reviews per parent_asin, pass 2 keeps the chosen reviews.
Sampling is reproducible: random.Random(SEED), sorted outputs, sort_keys=True.

Dataset: Hou et al. 2024, "Bridging Language and Items for Retrieval and
Recommendation", arXiv:2403.03952. No license is declared; academic,
non-commercial use only.
"""
from __future__ import annotations

import argparse
import collections
import gzip
import json
import platform
import random
import shutil
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw"
SEED = 42

# Fields kept from each record (the real files use `timestamp` in Unix ms and `helpful_vote`).
REVIEW_FIELDS = ["parent_asin", "asin", "rating", "title", "text", "timestamp", "helpful_vote", "verified_purchase", "user_id"]
META_FIELDS = ["parent_asin", "title", "store", "price", "average_rating", "rating_number", "main_category", "categories", "features"]


def review_url(category: str) -> str:
    return f"{BASE}/review_categories/{category}.jsonl.gz"


def meta_url(category: str) -> str:
    return f"{BASE}/meta_categories/meta_{category}.jsonl.gz"


def fetch(url: str, cache_dir: Path) -> Path:
    """Stream a URL to the cache directory in 1 MB chunks (skip if already cached)."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest = cache_dir / url.rsplit("/", 1)[-1]
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    tmp = dest.with_suffix(dest.suffix + ".part")
    print(f"downloading {url}", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=120) as resp, open(tmp, "wb") as out:
        shutil.copyfileobj(resp, out, length=1 << 20)
    tmp.replace(dest)
    return dest


def iter_jsonl_gz(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def dump_jsonl(rows, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n")


def clean_review(r: dict, max_chars: int) -> dict:
    out = {k: r.get(k) for k in REVIEW_FIELDS}
    out["text"] = (out["text"] or "").replace("<br />", " ").replace("<br/>", " ").strip()[:max_chars]
    out["title"] = (out["title"] or "").strip()
    out["helpful_vote"] = int(out["helpful_vote"] or 0)
    out["rating"] = float(out["rating"])
    out["timestamp"] = int(out["timestamp"])
    return out


def clean_meta(m: dict) -> dict:
    out = {k: m.get(k) for k in META_FIELDS}
    out["features"] = (out.get("features") or [])[:5]
    out["categories"] = out.get("categories") or []
    price = out.get("price")
    try:
        out["price"] = float(price) if price not in (None, "", "None") else None
    except (TypeError, ValueError):
        out["price"] = None
    return out


def sample_category(category: str, cache: Path, n_top: int, n_tail: int, tail_min: int,
                    per_product: int, max_chars: int, rng: random.Random):
    rpath = fetch(review_url(category), cache)
    mpath = fetch(meta_url(category), cache)

    # Pass 1: count usable reviews per product.
    counts = collections.Counter(
        r["parent_asin"] for r in iter_jsonl_gz(rpath) if (r.get("text") or "").strip()
    )
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    top = [a for a, _ in ranked[:n_top]]
    tail_pool = sorted(a for a, c in ranked[n_top:] if c >= tail_min)
    tail = rng.sample(tail_pool, min(n_tail, len(tail_pool)))

    # Metadata for the chosen products (left join: some items lack metadata).
    chosen = set(top) | set(tail)
    meta = {}
    for m in iter_jsonl_gz(mpath):
        if m.get("parent_asin") in chosen:
            meta[m["parent_asin"]] = clean_meta(m)
    # Keep only products that have metadata (titles are needed in the UI).
    chosen = {a for a in chosen if a in meta}

    # Pass 2: collect reviews of chosen products, then down-sample per product.
    per = collections.defaultdict(list)
    for r in iter_jsonl_gz(rpath):
        a = r.get("parent_asin")
        if a in chosen and (r.get("text") or "").strip():
            per[a].append(clean_review(r, max_chars))
    reviews = []
    for a in sorted(per):
        rows = sorted(per[a], key=lambda x: (x["timestamp"], x["user_id"], x["asin"]))
        if len(rows) > per_product:
            rows = rng.sample(rows, per_product)
        reviews.extend(rows)
    reviews.sort(key=lambda x: (x["parent_asin"], x["timestamp"], x["user_id"]))
    metas = [meta[a] for a in sorted(chosen)]
    stats = {
        "category": category, "n_top": len([a for a in top if a in chosen]),
        "n_tail": len([a for a in tail if a in chosen]),
        "raw_products": len(counts), "raw_reviews": sum(counts.values()),
    }
    return reviews, metas, stats


def write_datacard(path: Path, stats: dict, reviews, metas, args) -> None:
    ts = [r["timestamp"] for r in reviews]
    fmt = lambda t: datetime.fromtimestamp(t / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    stars = collections.Counter(int(r["rating"]) for r in reviews)
    n_price = sum(1 for m in metas if m["price"] is not None)
    text = f"""# DATACARD: data/sample/

Generated by `python scripts/prepare_data.py` (seed {SEED}, Python {platform.python_version()}).
Never regenerated on Netlify: the build reads these committed files only.

## Source
- Dataset: **Amazon Reviews 2023** (McAuley Lab), https://amazon-reviews-2023.github.io/
- Category: **{stats['category']}** (reviews: {stats['raw_reviews']:,} over {stats['raw_products']:,} products in the raw file)
- Reviews: {review_url(stats['category'])}
- Metadata: {meta_url(stats['category'])}
- Category chosen with `--category` (default All_Beauty). The raw files are cached in `data/raw/` (gitignored) and streamed twice.

## Sampling
- Top {args.n_top} products by number of non-empty reviews ({stats['n_top']} kept with metadata), plus {args.n_tail} random long-tail products with >= {args.tail_min} reviews ({stats['n_tail']} kept), drawn with `random.Random({SEED})`.
- Up to {args.per_product} reviews per product (random without replacement), review text truncated to {args.max_chars} characters, HTML `<br />` removed, empty texts dropped.
- Products without metadata are dropped (the dataset notes that some items lack metadata).

## Contents
| File | Rows |
|---|---|
| reviews.jsonl | {len(reviews):,} reviews |
| meta.jsonl | {len(metas):,} products ({n_price} with a price; `price` is null otherwise) |

- Date range: {fmt(min(ts))} to {fmt(max(ts))} (field `timestamp`, Unix **milliseconds**).
- Star distribution: {', '.join(f'{k}★ {stars.get(k, 0):,}' for k in range(1, 6))}.
- Review fields: {', '.join(REVIEW_FIELDS)}.
- Metadata fields: {', '.join(META_FIELDS)} (`features` truncated to 5 bullets).

## Caveats
- **No sales figures** exist in the data. `rating_number` and review counts are **proxies** for sales.
- The sample over-represents popular products by design (top-N), plus a random tail for "under-marketed gem" detection.
- Stars are a weak proxy for sentiment labels (used in docs/evaluation.md).

## Citation and license
Hou, Y., Li, J., He, Z., Yan, A., Chen, X., & McAuley, J. (2024). *Bridging Language and Items for Retrieval and Recommendation.* arXiv:2403.03952. https://arxiv.org/abs/2403.03952

No license is declared for the dataset. This sample is used for **academic, non-commercial** purposes only.
"""
    path.write_text(text, encoding="utf-8")


def make_fixtures(cache: Path, out_dir: Path, rng: random.Random) -> None:
    """30 reviews (5 products x 6) from the small Subscription_Boxes category."""
    reviews, metas, _ = sample_category(
        "Subscription_Boxes", cache, n_top=5, n_tail=0, tail_min=1, per_product=6, max_chars=800, rng=rng)
    dump_jsonl(reviews, out_dir / "reviews.jsonl")
    dump_jsonl(metas, out_dir / "meta.jsonl")
    (out_dir / "README.md").write_text(
        "# tests/fixtures\n\n"
        f"{len(reviews)} reviews over {len(metas)} products from Amazon Reviews 2023 `Subscription_Boxes` "
        "(Hou et al. 2024, arXiv:2403.03952; no license declared, academic use only).\n"
        "Generated by `python scripts/prepare_data.py` (seed 42). Same schema as `data/sample/`.\n",
        encoding="utf-8")
    print(f"fixtures: {len(reviews)} reviews, {len(metas)} products -> {out_dir}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--category", default="All_Beauty")
    p.add_argument("--cache-dir", type=Path, default=ROOT / "data" / "raw")
    p.add_argument("--out-dir", type=Path, default=ROOT / "data" / "sample")
    p.add_argument("--fixtures-dir", type=Path, default=ROOT / "tests" / "fixtures")
    p.add_argument("--n-top", type=int, default=150)
    p.add_argument("--n-tail", type=int, default=50)
    p.add_argument("--tail-min", type=int, default=20)
    p.add_argument("--per-product", type=int, default=60)
    p.add_argument("--max-chars", type=int, default=1500)
    p.add_argument("--skip-fixtures", action="store_true")
    args = p.parse_args(argv)

    reviews, metas, stats = sample_category(
        args.category, args.cache_dir, args.n_top, args.n_tail, args.tail_min,
        args.per_product, args.max_chars, random.Random(SEED))
    dump_jsonl(reviews, args.out_dir / "reviews.jsonl")
    dump_jsonl(metas, args.out_dir / "meta.jsonl")
    write_datacard(args.out_dir / "DATACARD.md", stats, reviews, metas, args)
    print(f"sample: {len(reviews)} reviews, {len(metas)} products -> {args.out_dir}")
    if not args.skip_fixtures:
        make_fixtures(args.cache_dir, args.fixtures_dir, random.Random(SEED))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
