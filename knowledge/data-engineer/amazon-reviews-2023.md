# Amazon Reviews 2023 (McAuley Lab)

Sources:
- https://amazon-reviews-2023.github.io/
- https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023
- https://arxiv.org/abs/2403.03952
- Live check: the first records of `Subscription_Boxes.jsonl.gz` and `meta_Subscription_Boxes.jsonl.gz`, streamed Nov 24 2026

## Review record (verified field names and types from the real file)
| Field | Type | Notes |
|---|---|---|
| `rating` | float | 1.0–5.0 |
| `title` | str | review title |
| `text` | str | review body |
| `images` | list | usually empty; ignore |
| `asin` | str | variant ID |
| `parent_asin` | str | **join key**: "Products with different colors, styles, sizes usually belong to the same parent ID... **Please use parent ID to find product meta.**" |
| `user_id` | str | anonymized |
| `timestamp` | int | **Unix time in milliseconds** (e.g. `1602133857705`). Convert with `pd.to_datetime(x, unit="ms", utc=True)` |
| `helpful_vote` | int | singular, as in the field table and the real file |
| `verified_purchase` | bool | |

⚠️ The website's "Quick Start" sample record shows `sort_timestamp` and `helpful_votes`, but the **real files use `timestamp` and `helpful_vote`**. Code against the real names.

## Metadata record (verified)
| Field | Type | Notes |
|---|---|---|
| `main_category` | str | e.g. "All Beauty", "SUBSCRIPTION BOXES" (casing varies) |
| `title` | str | product title |
| `average_rating` | float | shown on the product page |
| `rating_number` | int | number of ratings: **the main popularity proxy** |
| `features` | list[str] | bullet points |
| `description` | list[str] | may be `[]` |
| `price` | float **or null** | "Price in US dollars (at time of crawling)". Often `None` |
| `images`, `videos` | list | ignore (or use a thumbnail URL) |
| `store` | str | brand or seller; seeds spaCy's EntityRuler |
| `categories` | list[str] | may be `[]` |
| `details` | dict | may be `{}` |
| `parent_asin` | str | join key |
| `bought_together` | list **or null** | often `None` |

"We count the number of items based on user reviews rather than item metadata files. Note that some items lack metadata." So **left-join** reviews to metadata and handle missing products.

## Downloads (direct, no login)
```
https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/review_categories/{Category}.jsonl.gz
https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/meta_categories/meta_{Category}.jsonl.gz
```
Category sizes (#users / #items / #ratings): All_Beauty 632.0K / 112.6K / 701.5K. Subscription_Boxes 15.2K / 641 / 16.2K (use for fixtures). Magazine_Subscriptions 60.1K / 3.4K / 71.5K. Full table: docs/03-dataset.md.

## Citation and license
- The dataset site's BibTeX:
  ```bibtex
  @article{hou2024bridging,
    title={Bridging Language and Items for Retrieval and Recommendation},
    author={Hou, Yupeng and Li, Jiacheng and He, Zhankui and Yan, An and Chen, Xiusi and McAuley, Julian},
    journal={arXiv preprint arXiv:2403.03952},
    year={2024}
  }
  ```
  The current arXiv version has the longer title "...: Benchmarking LLMs as Semantic Encoders" and adds the author Xiangjun Fu. Cite the dataset site's BibTeX and mention the arXiv ID.
- **No license is declared** (no `license:` field on the HF card). Use the data for academic, non-commercial work only, commit only a small sample, and give the citation.
