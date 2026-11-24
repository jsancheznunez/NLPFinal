"""Netlify build entrypoint: run spaCy + NLTK + metrics over data/sample/ and write static JSON.

    pip install -r requirements.txt && python scripts/build_analysis.py

Netlify runs this with Python 3.12 (netlify.toml) and publishes site/. Outputs:
  site/data/{summary,products,aspects,trends,nltk_examples,build_info}.json
  site/data/product/<parent_asin>.json
  site/displacy/dep-<i>.svg, site/displacy/entities.html     (spaCy displaCy, pre-rendered)
  site/py/nltk_layer.py                                      (same file the browser imports)
  site/nltk_data/{sentiment,corpora,tokenizers}/*.zip        (mounted by Pyodide)

Every JSON file is validated against schemas/*.schema.json (the build fails on any
error) and written with allow_nan=False, sort_keys=True, so reruns are byte-identical
(except build_info.json, which holds timings).
Notes: knowledge/build-pipeline-engineer/build-script.md.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import platform
import shutil
import sys
import time
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

NLTK_PACKAGES = [("sentiment", "vader_lexicon"), ("corpora", "stopwords"), ("tokenizers", "punkt_tab")]
DATASET_CITATION = ("Hou, Y., Li, J., He, Z., Yan, A., Chen, X., & McAuley, J. (2024). Bridging Language and "
                    "Items for Retrieval and Recommendation. arXiv:2403.03952.")
LICENSE_NOTE = "No license is declared for Amazon Reviews 2023; used for academic, non-commercial purposes only."
PRICE_ASPECTS = {"price", "value", "cost", "money"}

# Hand-written texts for the playground's example buttons and the build/browser parity test.
CURATED = [
    ("curated-positive", "Absolutely love this coffee! It tastes rich and smooth and the aroma is amazing. Will buy again :)"),
    ("curated-negative", "Terrible quality. The bag arrived torn and the crackers were stale. Not worth the price."),
    ("curated-mixed", "The flavor is delicious, but the packaging is cheap and the jar leaked everywhere."),
    ("curated-negation", "Not bad at all, though it isn't great either. The sauce is not too spicy."),
    ("curated-neutral", "Arrived on Tuesday. The box contains two bags of rice and one bottle of olive oil."),
]


def log(msg: str) -> None:
    print(f"[build] {msg}", flush=True)


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, allow_nan=False, separators=(",", ":"), sort_keys=True)


def read_jsonl(path: Path) -> list:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


# --------------------------------------------------------------------------- NLTK data
def ensure_nltk_data(nltk_dir: Path) -> None:
    """Make sure vader_lexicon, stopwords and punkt_tab exist (download once, quietly, at build time only)."""
    import nltk
    nltk_dir.mkdir(parents=True, exist_ok=True)
    if str(nltk_dir) not in nltk.data.path:
        nltk.data.path.insert(0, str(nltk_dir))
    for cat, name in NLTK_PACKAGES:
        if not (nltk_dir / cat / f"{name}.zip").exists():
            log(f"downloading NLTK package {name} -> {nltk_dir}")
            ok = nltk.download(name, download_dir=str(nltk_dir), quiet=True, raise_on_error=True)
            if not ok:
                raise SystemExit(f"could not download NLTK package {name}")


def deterministic_zip(members: list, dest: Path) -> None:
    """Write a zip with fixed timestamps so the output is byte-stable."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for arcname, data in sorted(members):
            info = zipfile.ZipInfo(arcname, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, data)
    dest.write_bytes(buf.getvalue())


def copy_browser_assets(nltk_dir: Path, site: Path) -> list:
    """nltk_layer.py -> site/py/; NLTK zips -> site/nltk_data/ (English-only subsets for size)."""
    written = []
    (site / "py").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "analyzer" / "nltk_layer.py", site / "py" / "nltk_layer.py")
    written.append("py/nltk_layer.py")
    out = site / "nltk_data"
    shutil.rmtree(out, ignore_errors=True)
    # VADER reads its lexicon straight from inside the zip: copy as-is.
    (out / "sentiment").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(nltk_dir / "sentiment" / "vader_lexicon.zip", out / "sentiment" / "vader_lexicon.zip")
    written.append("nltk_data/sentiment/vader_lexicon.zip")
    # stopwords + punkt_tab: keep only the English files (punkt_tab.zip is 4.3 MB with all languages).
    for cat, name, keep in [("corpora", "stopwords", ("stopwords/english", "stopwords/README")),
                            ("tokenizers", "punkt_tab", ("punkt_tab/english/", "punkt_tab/README"))]:
        with zipfile.ZipFile(nltk_dir / cat / f"{name}.zip") as zf:
            members = [(n, zf.read(n)) for n in zf.namelist()
                       if not n.endswith("/") and n.startswith(keep)]
            dirs = sorted({n.rsplit("/", 1)[0] + "/" for n, _ in members})
        members += [(d, b"") for d in dirs if d.count("/") >= 1]
        deterministic_zip(members, out / cat / f"{name}.zip")
        written.append(f"nltk_data/{cat}/{name}.zip")
    return written


# --------------------------------------------------------------------------- helpers
def mix(labels) -> dict:
    c = Counter(labels)
    n = max(sum(c.values()), 1)
    return {k: round(c.get(k, 0) / n, 4) for k in ("positive", "neutral", "negative")}


def aspect_items(pairs: list, min_mentions: int, n: int, with_products: bool = False) -> list:
    """pairs: dicts with aspect, opinion, negated, compound, parent_asin."""
    by = defaultdict(list)
    for p in pairs:
        by[p["aspect"]].append(p)
    items = []
    for asp, ps in by.items():
        if len(ps) < min_mentions:
            continue
        comps = [p["compound"] for p in ps]
        ops = Counter(("not " if p["negated"] else "") + p["opinion"] for p in ps)
        item = {
            "aspect": asp,
            "mentions": len(ps),
            "mean_compound": round(sum(comps) / len(comps), 4),
            "pct_negative": round(sum(1 for c in comps if c <= -0.05) / len(comps), 4),
            "top_opinions": [{"text": t, "count": k} for t, k in sorted(ops.items(), key=lambda kv: (-kv[1], kv[0]))[:5]],
        }
        if with_products:
            item["n_products"] = len({p["parent_asin"] for p in ps})
        items.append(item)
    items.sort(key=lambda it: (-it["mentions"], it["aspect"]))
    return items[:n]


def ranked_aspects(items: list, n: int, negative: bool) -> list:
    """Negative = highest share of VADER-negative mentions (reviews skew positive, so few
    aspects have a mean below 0); positive = highest mean compound."""
    if negative:
        pool = [it for it in items if it["pct_negative"] > 0]
        pool.sort(key=lambda it: (-it["pct_negative"], it["mean_compound"], -it["mentions"], it["aspect"]))
    else:
        pool = [it for it in items if it["mean_compound"] > 0]
        pool.sort(key=lambda it: (-it["mean_compound"], -it["mentions"], it["aspect"]))
    return pool[:n]


def example(review, comp) -> dict:
    from datetime import datetime, timezone
    return {
        "text": review["text"][:600],
        "rating": float(review["rating"]),
        "compound": comp,
        "helpful_vote": int(review["helpful_vote"]),
        "date": datetime.fromtimestamp(review["timestamp"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d"),
    }


def pick_displacy_sentences(reviews, feats, compounds, n: int = 6) -> list:
    """Short, clean sentences that show the dependency rules: positive, negative, negated, 'but'."""
    cands = {"pos": [], "neg": [], "negated": [], "but": []}
    for r, f, c in zip(reviews, feats, compounds):
        for s in f["sentences"]:
            t = s["text"]
            if not (35 <= len(t) <= 95) or not s["pairs"] or "\n" in t or not t[0].isupper():
                continue
            if any(p["negated"] for p in s["pairs"]):
                cands["negated"].append(t)
            elif " but " in t:
                cands["but"].append(t)
            elif c >= 0.5:
                cands["pos"].append(t)
            elif c <= -0.5:
                cands["neg"].append(t)
    for k in cands:
        cands[k] = sorted(set(cands[k]), key=lambda t: (len(t), t))
    order = ["pos", "neg", "negated", "but", "pos", "neg"]
    picked, used = [], Counter()
    for k in order:
        pool = cands[k]
        if used[k] < len(pool):
            picked.append(pool[used[k]])
            used[k] += 1
    return picked[:n]


# --------------------------------------------------------------------------- main
def sample_category(data_dir: Path) -> str:
    """Category name recorded by prepare_data.py in DATACARD.md ("- Category: **X**")."""
    card = data_dir / "DATACARD.md"
    if card.is_file():
        for line in card.read_text(encoding="utf-8").splitlines():
            if line.startswith("- Category: **"):
                return line.split("**")[1]
    return "unknown"


def build(data_dir: Path, site: Path, nltk_dir: Path, budget: float) -> dict:
    timings = {}
    t0 = time.perf_counter()

    def lap(name, start):
        timings[name] = round(time.perf_counter() - start, 3)
        log(f"{name}: {timings[name]:.2f}s")

    # 1) NLTK data -----------------------------------------------------------------
    t = time.perf_counter()
    ensure_nltk_data(nltk_dir)
    import nltk  # noqa: F401  (path set above)
    from analyzer import contract, metrics, nltk_layer, spacy_layer
    import pandas as pd
    lap("nltk_data", t)

    # 2) Load the committed sample -------------------------------------------------
    t = time.perf_counter()
    reviews = read_jsonl(data_dir / "reviews.jsonl")
    metas = read_jsonl(data_dir / "meta.jsonl")
    meta_by = {m["parent_asin"]: m for m in metas}
    reviews = [r for r in reviews if r["parent_asin"] in meta_by and (r.get("text") or "").strip()]
    reviews.sort(key=lambda r: (r["parent_asin"], r["timestamp"], r.get("user_id") or ""))
    log(f"sample: {len(reviews)} reviews, {len(meta_by)} products from {data_dir}")
    lap("load", t)

    # 3) spaCy: one nlp.pipe pass ---------------------------------------------------
    t = time.perf_counter()
    common = frozenset(nltk_layer.sia().lexicon) | nltk_layer.stopword_set()  # e.g. a store named "Okay"
    nlp = spacy_layer.load_nlp(spacy_layer.build_patterns(metas, common))
    model = spacy_layer.model_version(nlp)
    feats = spacy_layer.process(nlp, (r["text"] for r in reviews))
    lap("spacy", t)

    # 4) NLTK: VADER per review and per aspect-opinion pair ----------------------------
    t = time.perf_counter()
    compounds = [nltk_layer.compound(r["text"]) for r in reviews]
    labels = [nltk_layer.label(c) for c in compounds]
    pairs_all = []
    neg_money = Counter()
    phrase_cache = {}
    for r, f, lab in zip(reviews, feats, labels):
        for s in f["sentences"]:
            if not s["pairs"]:
                continue
            sent_c = None
            for p in s["pairs"]:
                phrase = ("not " if p["negated"] else "") + p["opinion"]
                if phrase not in phrase_cache:
                    phrase_cache[phrase] = nltk_layer.compound(phrase)
                c = phrase_cache[phrase]
                if c == 0.0:  # opinion word not in the VADER lexicon: fall back to its sentence
                    if sent_c is None:
                        sent_c = nltk_layer.compound(s["text"])
                    c = sent_c
                pairs_all.append({**p, "compound": c, "parent_asin": r["parent_asin"]})
        if lab == "negative":
            neg_money[r["parent_asin"]] += sum(1 for _, l in f["entities"] if l == "MONEY")
    lap("nltk", t)

    # 5) Per-product aggregation --------------------------------------------------------
    t = time.perf_counter()
    by_product = defaultdict(list)
    for i, r in enumerate(reviews):
        by_product[r["parent_asin"]].append(i)
    pairs_by = defaultdict(list)
    for p in pairs_all:
        pairs_by[p["parent_asin"]].append(p)

    aspect_signals, product_aspects = {}, {}
    for asin, ps in pairs_by.items():
        items = aspect_items(ps, min_mentions=2, n=25)
        product_aspects[asin] = items
        neg = ranked_aspects(items, 1, negative=True)
        neg_price = sum(1 for p in ps if p["aspect"] in PRICE_ASPECTS and p["compound"] <= -0.05)
        aspect_signals[asin] = {"top_negative_aspect": neg[0]["aspect"] if neg else None,
                                "neg_price_mentions": neg_price + neg_money.get(asin, 0)}

    rdf = pd.DataFrame({
        "parent_asin": [r["parent_asin"] for r in reviews],
        "rating": [float(r["rating"]) for r in reviews],
        "timestamp": [int(r["timestamp"]) for r in reviews],
        "helpful_vote": [int(r["helpful_vote"]) for r in reviews],
        "compound": compounds,
    })
    mdf = pd.DataFrame([{"parent_asin": a, "rating_number": m.get("rating_number"),
                         "average_rating": m.get("average_rating"), "price": m.get("price")}
                        for a, m in sorted(meta_by.items())])
    mdf["price"] = pd.to_numeric(mdf["price"], errors="coerce")
    table = metrics.product_table(rdf, mdf, aspect_signals)
    as_of = table.attrs["data_as_of"]
    tdf = metrics.add_time(rdf)
    lap("metrics", t)

    # 6) Assemble JSON documents ----------------------------------------------------------
    t = time.perf_counter()
    outputs = {}
    rows = []
    for _, row in table.iterrows():
        asin = row["parent_asin"]
        m = meta_by[asin]
        idx = by_product[asin]
        p_labels = [labels[i] for i in idx]
        ents = [e for i in idx for e in feats[i]["entities"]]
        items = product_aspects.get(asin, [])
        price = metrics.r4(row["price"])
        rn = row["rating_number"]
        metrics_section = {
            "source": "metrics", "metric_kind": "proxy",
            "rating_number": None if pd.isna(rn) else int(rn),
            "average_rating": metrics.r4(row["average_rating"]),
            "n_reviews": int(row["n_reviews"]),
            "mean_rating": metrics.r4(row["mean_rating"]),
            "adj_rating": metrics.r4(row["adj_rating"]),
            "velocity": metrics.r4(row["velocity"]),
            "recent_reviews": int(row["recent_reviews"]),
            "best_seller_rank": int(row["best_seller_rank"]),
            "score": metrics.r4(row["score"]),
            "rank": int(row["rank"]),
            "price_band": row["price_band"],
            "flags": list(row["flags"]),
        }
        nltk_section = {"source": "nltk", "mean_compound": metrics.r4(row["mean_compound"]),
                        "pct_negative": metrics.r4(row["pct_negative"]), "sentiment_mix": mix(p_labels)}
        top_ents = spacy_layer.count_entities(ents, 5)
        brief = lambda its: [{"aspect": a["aspect"], "mentions": a["mentions"], "mean_compound": a["mean_compound"]} for a in its]
        rows.append({
            "parent_asin": asin, "title": m.get("title") or asin, "store": m.get("store") or None, "price": price,
            "metrics": metrics_section, "nltk": nltk_section,
            "spacy": {"source": "spacy", "n_entities": len(ents), "top_entities": top_ents},
            "aspects": {"source": "spacy+nltk", "top_negative": brief(ranked_aspects(items, 3, True)),
                        "top_positive": brief(ranked_aspects(items, 3, False))},
        })

        # product/<asin>.json
        pos_l = [s["lemmas"] for i in idx if labels[i] == "positive" for s in feats[i]["sentences"]]
        neg_l = [s["lemmas"] for i in idx if labels[i] == "negative" for s in feats[i]["sentences"]]
        sub = tdf[tdf["parent_asin"] == asin]
        months = metrics.month_range(as_of, 24)
        hist = Counter(int(reviews[i]["rating"]) for i in idx)

        def best(lab):
            cand = [i for i in idx if labels[i] == lab]
            if not cand:
                return None
            i = sorted(cand, key=lambda i: (-reviews[i]["helpful_vote"], -abs(compounds[i]), reviews[i]["timestamp"]))[0]
            return example(reviews[i], compounds[i])

        outputs[f"product/{asin}.json"] = ("product", {
            "parent_asin": asin, "title": m.get("title") or asin, "store": m.get("store") or None, "price": price,
            "metrics": {**metrics_section, "monthly": metrics.monthly_ratings(sub, months),
                        "rating_histogram": {str(k): int(hist.get(k, 0)) for k in range(1, 6)}},
            "nltk": {**nltk_section,
                     "top_terms": {"positive": nltk_layer.top_terms(pos_l, 12), "negative": nltk_layer.top_terms(neg_l, 12)},
                     "collocations": {"measure": "likelihood_ratio", "min_freq": 3,
                                      "positive": nltk_layer.key_phrases(pos_l, 8, 3),
                                      "negative": nltk_layer.key_phrases(neg_l, 8, 3)},
                     "monthly_sentiment": metrics.monthly_sentiment(sub, months),
                     "examples": {"most_helpful_positive": best("positive"), "most_helpful_negative": best("negative")}},
            "spacy": {"source": "spacy", "model": model, "n_entities": len(ents),
                      "entities": spacy_layer.count_entities([e for e in ents if e[1] not in ("BRAND", "PRODUCT")], 12),
                      "brands": spacy_layer.count_items([e[0] for e in ents if e[1] == "BRAND"], 8),
                      "products": spacy_layer.count_items([e[0] for e in ents if e[1] == "PRODUCT"], 8),
                      "noun_chunks": spacy_layer.count_items([c for i in idx for c in feats[i]["noun_chunks"]], 15)},
            "aspects": {"source": "spacy+nltk", "n_pairs": len(pairs_by.get(asin, [])), "items": items},
        })

    weights = dict(metrics.WEIGHTS)
    outputs["products.json"] = ("products", {"metric_kind": "proxy", "weights": weights, "products": rows})

    cat_aspects = aspect_items(pairs_all, min_mentions=8, n=60, with_products=True)
    outputs["aspects.json"] = ("aspects", {
        "source": "spacy+nltk",
        "method": ("spaCy en_core_web_sm dependency rules (amod; acomp + nsubj; opinion verb + dobj; conj; neg) "
                   "extract (aspect, opinion, negated); NLTK VADER scores the opinion phrase "
                   "('not ' prefixed when negated), falling back to the sentence when the word is not in the lexicon."),
        "n_pairs": len(pairs_all), "items": cat_aspects,
    })

    all_pos = [s["lemmas"] for f, l in zip(feats, labels) if l == "positive" for s in f["sentences"]]
    all_neg = [s["lemmas"] for f, l in zip(feats, labels) if l == "negative" for s in f["sentences"]]
    all_ents = [e for f in feats for e in f["entities"]]
    opportunities = []
    for _, row in table.iterrows():
        for flag, reason in zip(row["flags"], row["flag_reasons"]):
            opportunities.append({"parent_asin": row["parent_asin"], "flag": flag, "reason": reason})
    opportunities.sort(key=lambda o: (o["flag"], o["parent_asin"]))
    outputs["summary.json"] = ("summary", {
        "schema_version": "1.0", "metric_kind": "proxy",
        "dataset": {"name": "Amazon Reviews 2023 (McAuley Lab)", "category": sample_category(data_dir),
                    "citation": DATASET_CITATION, "url": "https://amazon-reviews-2023.github.io/",
                    "license_note": LICENSE_NOTE, "data_as_of": as_of.strftime("%Y-%m-%d"),
                    "n_products": len(rows), "n_reviews": len(reviews), "simulated": False},
        "nltk": {"source": "nltk",
                 "method": "VADER compound on each review (thresholds +/-0.05); FreqDist and likelihood-ratio "
                           "bigram collocations over spaCy lemmas with ecommerce stopwords (negations kept).",
                 "thresholds": {"positive": 0.05, "negative": -0.05},
                 "mean_compound": round(sum(compounds) / len(compounds), 4), "sentiment_mix": mix(labels),
                 "top_terms": {"positive": nltk_layer.top_terms(all_pos, 20), "negative": nltk_layer.top_terms(all_neg, 20)},
                 "collocations": {"measure": "likelihood_ratio", "min_freq": 5,
                                  "positive": nltk_layer.key_phrases(all_pos, 15, 5),
                                  "negative": nltk_layer.key_phrases(all_neg, 15, 5)}},
        "spacy": {"source": "spacy", "model": model, "n_entities": len(all_ents),
                  "top_entities": spacy_layer.count_entities([e for e in all_ents if e[1] not in ("BRAND", "PRODUCT")], 20),
                  "top_brands": spacy_layer.count_items([e[0] for e in all_ents if e[1] == "BRAND"], 15),
                  "top_noun_chunks": spacy_layer.count_items([c for f in feats for c in f["noun_chunks"]], 20)},
        "aspects": {"source": "spacy+nltk", "n_pairs": len(pairs_all),
                    "top_negative": ranked_aspects(cat_aspects, 10, True),
                    "top_positive": ranked_aspects(cat_aspects, 10, False)},
        "metrics": {"source": "metrics", "metric_kind": "proxy", "weights": weights, "weights_note": metrics.WEIGHTS_NOTE,
                    "best_sellers": [r["parent_asin"] for r in sorted(rows, key=lambda r: r["metrics"]["best_seller_rank"])[:15]],
                    "top_performers": [r["parent_asin"] for r in rows[:15]],
                    "opportunities": opportunities},
    })

    # trends.json: last 36 months of the sample
    months = metrics.month_range(as_of, 36)
    prev_start, recent_start = metrics.windows(as_of)
    ts_list = tdf["ts"].tolist()
    recent_idx = [i for i, ts in enumerate(ts_list) if ts > recent_start]
    recent_docs = [s["lemmas"] for i in recent_idx for s in feats[i]["sentences"]]
    prev_docs = [s["lemmas"] for f, ts in zip(feats, ts_list) if prev_start < ts <= recent_start for s in f["sentences"]]
    fd_r, fd_p = nltk_layer.freq_table(recent_docs), nltk_layer.freq_table(prev_docs)
    spread = defaultdict(set)  # a trending term must appear in >= 3 products (not one product's buzzword)
    for i in recent_idx:
        for s in feats[i]["sentences"]:
            for w in nltk_layer.content_words(s["lemmas"]):
                spread[w].add(reviews[i]["parent_asin"])
    trending = []
    for term, cnt in fd_r.items():
        if cnt >= 5 and len(spread[term]) >= 3 and term not in nltk_layer.NEGATION_TERMS:
            rf, pf = fd_r.freq(term), fd_p.freq(term)
            trending.append({"term": term, "recent_freq": round(rf, 4), "previous_freq": round(pf, 4),
                             "delta": round(rf - pf, 4), "recent_count": int(cnt)})
    trending.sort(key=lambda x: (-x["delta"], x["term"]))
    outputs["trends.json"] = ("trends", {
        "metrics": {"source": "metrics", "metric_kind": "proxy", "monthly": metrics.monthly_ratings(tdf, months)},
        "nltk": {"source": "nltk", "window": f"last 6 months vs previous 6 months (data as of {as_of.strftime('%Y-%m-%d')})",
                 "monthly_sentiment": metrics.monthly_sentiment(tdf, months, with_neg=True),
                 "trending_terms": trending[:20]},
    })

    # nltk_examples.json: curated texts + one sample review per star rating
    ex = list(CURATED)
    for star in range(1, 6):
        cand = sorted((r for r in reviews if int(r["rating"]) == star and 80 <= len(r["text"]) <= 300),
                      key=lambda r: (-r["helpful_vote"], r["parent_asin"], r["timestamp"]))
        if cand:
            ex.append((f"review-{star}star", cand[0]["text"]))
    rating_of = {r["text"]: float(r["rating"]) for r in reviews}
    outputs["nltk_examples.json"] = ("nltk_examples", {
        "source": "nltk", "nltk_version": nltk_layer.NLTK_VERSION,
        "items": [{"id": i, "text": txt, "rating": rating_of.get(txt), "result": nltk_layer.analyze(txt)} for i, txt in ex],
    })
    lap("assemble", t)

    # 7) Validate everything, then write ------------------------------------------------
    t = time.perf_counter()
    failures = []
    for rel, (schema, obj) in outputs.items():
        errs = contract.errors(schema, obj)
        if errs:
            failures.append(f"{rel}: " + "; ".join(errs[:3]))
    if failures:
        for f in failures[:20]:
            log(f"SCHEMA ERROR {f}")
        raise SystemExit(f"schema validation failed for {len(failures)} file(s)")
    data_dir_out = site / "data"
    shutil.rmtree(data_dir_out, ignore_errors=True)
    (data_dir_out / "product").mkdir(parents=True, exist_ok=True)
    for rel, (_, obj) in sorted(outputs.items()):
        (data_dir_out / rel).write_text(dumps(obj) + "\n", encoding="utf-8")
    log(f"validated + wrote {len(outputs)} JSON files to {data_dir_out}")
    lap("validate_write", t)

    # 8) displaCy + browser assets ---------------------------------------------------------
    t = time.perf_counter()
    shutil.rmtree(site / "displacy", ignore_errors=True)
    sents = pick_displacy_sentences(reviews, feats, compounds)
    disp = spacy_layer.render_displacy(nlp, sents, site / "displacy")
    (site / "displacy" / "sentences.json").write_text(dumps({"source": "spacy", "model": model, "sentences": sents}) + "\n",
                                                      encoding="utf-8")
    assets = copy_browser_assets(nltk_dir, site)
    lap("displacy_assets", t)

    total = round(time.perf_counter() - t0, 3)
    import importlib.metadata
    import spacy
    info = {
        "commit_ref": os.environ.get("COMMIT_REF"),
        "context": os.environ.get("CONTEXT", "local"),
        "python": platform.python_version(),
        "versions": {"nltk": nltk_layer.NLTK_VERSION, "spacy": spacy.__version__, "en_core_web_sm": model,
                     "pandas": pd.__version__, "jsonschema": importlib.metadata.version("jsonschema")},
        "sample": {"n_products": len(rows), "n_reviews": len(reviews), "data_dir": os.path.relpath(data_dir, ROOT)},
        "timings": timings, "total_seconds": total, "budget_seconds": budget,
        "outputs": sorted(outputs) + [f"displacy/{d}" for d in disp] + assets,
    }
    contract.validate("build_info", info)
    (data_dir_out / "build_info.json").write_text(dumps(info) + "\n", encoding="utf-8")
    log(f"total: {total:.2f}s (budget {budget:.0f}s); {len(outputs)} JSON files, {len(disp)} displaCy files, "
        f"{len(pairs_all)} aspect pairs")
    if total > budget:
        raise SystemExit(f"build took {total:.1f}s, over the {budget:.0f}s budget")
    return info


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Build static NLP analysis JSON for the site.")
    p.add_argument("--data-dir", type=Path, default=ROOT / "data" / "sample")
    p.add_argument("--site-dir", type=Path, default=ROOT / "site")
    p.add_argument("--nltk-data", type=Path, default=Path(os.environ.get("NLTK_DATA_DIR", ROOT / "nltk_data")))
    p.add_argument("--budget", type=float, default=float(os.environ.get("BUILD_BUDGET_SECONDS", 600)))
    args = p.parse_args(argv)
    build(args.data_dir.resolve(), args.site_dir.resolve(), args.nltk_data.resolve(), args.budget)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
