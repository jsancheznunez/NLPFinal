# 03 — Free, Public Review Dataset

## Recommendation

**Primary: Amazon Reviews 2023 (McAuley Lab, UC San Diego). Use one or two small categories.**

This dataset has the three things the analyzer needs:
- **Customer reviews:** star rating, title, text, helpful votes, verified purchase, timestamp
- **Product information:** title, price, store/brand, categories, features, description, average rating, rating count
- **A shared key:** `parent_asin` joins reviews to products

It is free, downloads directly (no login), and is widely cited in academic NLP and recommender-systems work.

**Backup / small demo set: Women's E-Commerce Clothing Reviews (Kaggle, CC0 public domain).** It has 23,486 reviews in a 2.5 MB CSV. Use it if the team wants a tiny, clearly licensed dataset for tests or the in-browser demo.

---

## A. Amazon Reviews 2023 (primary)

- Homepage and downloads: https://amazon-reviews-2023.github.io/
- Hugging Face mirror: https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023
- Paper: Hou, Y., Li, J., He, Z., Yan, A., Chen, X., & McAuley, J. (2024). *Bridging Language and Items for Retrieval and Recommendation.* arXiv:2403.03952
- Scale: 571.54M reviews across 33 categories, May 1996 – Sep 2023. We only need a slice.

### Fields

**Review file** (`{Category}.jsonl.gz`), one JSON object per line:

| Field | Use in the analyzer |
|---|---|
| `rating` (1–5) | Weak sentiment label; rating distribution |
| `title`, `text` | **NLP input** (concatenate `title + ". " + text`) |
| `images` | (ignore) |
| `asin`, `parent_asin` | Product key. **Use `parent_asin` to join with metadata** (the dataset authors say so explicitly) |
| `user_id` | Repeat-reviewer counts (optional) |
| `timestamp` (Unix **milliseconds**, verified against the real file) | Trends over time and review velocity |
| `verified_purchase` | Filter or weight verified reviews; data-quality panel |
| `helpful_vote` | Weight helpful reviews more; surface "most helpful complaint" |

**Metadata file** (`meta_{Category}.jsonl.gz`):

| Field | Use |
|---|---|
| `parent_asin` | Join key |
| `title`, `features`, `description` | Product info; spaCy NER for brand names |
| `main_category`, `categories` | Category roll-ups and trends |
| `price` | Price-band analysis; price vs. sentiment (often missing or `None`, so handle it) |
| `store` | Brand/seller; seeds the spaCy `EntityRuler` |
| `average_rating`, `rating_number` | Product-level popularity and quality |
| `details` | Dict of attributes (e.g. "Date First Available") |
| `bought_together` | Cross-sell opportunities (often empty) |
| `images`, `videos` | (ignore, or show a thumbnail URL in the UI) |

### Suggested categories (pick by size)

| Category | #Users | #Items | #Ratings | Notes |
|---|---|---|---|---|
| **All_Beauty** | 632.0K | 112.6K | 701.5K | **Recommended default.** Varied, opinion-rich text (scent, skin, packaging). |
| Health_and_Personal_Care | 461.7K | 60.3K | 494.1K | Good alternative |
| Appliances | 1.8M | 94.3K | 2.1M | Great for durability, competitor brands and NER. Larger |
| Amazon_Fashion | 2.0M | 825.9K | 2.5M | Sizing and fit aspects. Metadata is large (510M tokens) |
| Software | 2.6M | 89.2K | 4.9M | Large |
| Handmade_Products | 586.6K | 164.7K | 664.2K | |
| Digital_Music | 101.0K | 70.5K | 130.4K | Small |
| Magazine_Subscriptions | 60.1K | 3.4K | 71.5K | Small, good for CI tests |
| Gift_Cards | 132.7K | 1.1K | 152.4K | Small, but reviews say little about the product |
| Subscription_Boxes | 15.2K | 641 | 16.2K | Tiny, good for unit tests |

### Download URLs (direct)

```
https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/review_categories/{Category}.jsonl.gz
https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/meta_categories/meta_{Category}.jsonl.gz
```
For example `.../review_categories/All_Beauty.jsonl.gz` and `.../meta_categories/meta_All_Beauty.jsonl.gz`.

> **Don't download these during the Netlify build.** They are hundreds of MB, and an external host makes builds slow and flaky. Instead, run a one-time **`scripts/prepare_data.py`** locally or in CI. It should stream the `.jsonl.gz` and **sample** the data, e.g. the top 300 products by review count and up to 100 reviews each (about 30k reviews). Write the sample to `data/sample/*.jsonl` (a few MB) and commit it. The Netlify build then runs NLP on that committed sample only.

The Hugging Face mirror uses a dataset loading script (`trust_remote_code=True`). Newer `datasets` versions have dropped support for those scripts, so **prefer the direct `.jsonl.gz` URLs above**.

### License and terms: what we found

**Confirmed (Nov 2026):** neither the dataset website nor the Hugging Face card declares a license. The card's YAML header has no `license:` field, and the Hub API returns no license tag. Common practice for the McAuley Lab Amazon datasets is **research and academic use, with the paper cited**. For a class project:
- Cite the paper (above) in the README and the report.
- Commit only a **small sample**. Don't redistribute the full dump.
- Don't use it commercially.
- Say in the report that no license is declared and that the data is used for non-commercial academic work, with citation.

### Important caveat: there are no sales numbers

Amazon Reviews 2023 has **no units sold or revenue**. The analyzer has to use clear **proxies** and say they are proxies in the UI and the report:

| Metric | Proxy formula |
|---|---|
| **Popularity / "best-seller" rank** | `rating_number` (total ratings) and the number of reviews in our sample. A review count is a reasonable demand proxy |
| **Review velocity (trend)** | reviews per month from `timestamp`. Growth over the last N months shows rising products |
| **Quality** | `average_rating` and a Bayesian-adjusted rating: `(v·R + m·C)/(v+m)`, where v = number of ratings, R = product mean, C = category mean, m = a prior (e.g. 20) |
| **Sentiment** | mean VADER `compound` and % negative (NLTK) |
| **Aspect health** | share of negative aspect mentions (spaCy + VADER) |
| **Performance score** | z-score each signal within its category, then take a weighted sum, e.g. 0.35·popularity + 0.25·adj. rating + 0.25·sentiment + 0.15·velocity. Show the weights in the UI |
| **Opportunity flags** | high popularity + low sentiment = "fix the top complaint"; high sentiment + low popularity = "under-marketed gem"; rising velocity = "trending" |

Optionally, add a small **synthetic `sales.csv`** (units and revenue per product per month) generated from review counts × a random conversion factor, **clearly labeled as simulated**. That lets the "sales data" part of the brief be shown without pretending it is real.

---

## B. Women's E-Commerce Clothing Reviews (backup / demo)

- Source: https://www.kaggle.com/datasets/nicapotato/womens-ecommerce-clothing-reviews. HF mirror without a Kaggle login: https://huggingface.co/datasets/chibifire/kaggle-womens-ecom-clothing-reviews
- License: **CC0-1.0 (public domain)**
- Size: **23,486 rows**, ~2.5 MB
- Columns: Clothing ID, Age, Title, Review Text, Rating, Recommended IND, Positive Feedback Count, Division Name, Department Name, Class Name
- Pros: tiny, clean license, has a "Recommended" label for evaluation, and is small enough to load straight into the browser (Pyodide) demo.
- Cons: no product titles, prices or timestamps, and the retailer is anonymized. Trend and price analysis isn't possible.

## C. Considered and not chosen

| Dataset | Why not |
|---|---|
| Olist Brazilian E-Commerce (Kaggle) | Has **real orders, prices and payments**, but the reviews are in **Portuguese**. VADER and `en_core_web_sm` are English-only. License is CC BY-NC-SA 4.0. Only worth it if the team switches to Portuguese models |
| Amazon Reviews 2018 / 2014 (McAuley) | Superseded by the 2023 release |
| Yelp Open Dataset | Businesses, not products, and the license terms are restrictive |

## Sources
- https://amazon-reviews-2023.github.io/ (fields, category table, download URLs)
- https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023 and arXiv:2403.03952
- https://huggingface.co/datasets/chibifire/kaggle-womens-ecom-clothing-reviews (CC0-1.0, 23,486 rows)
