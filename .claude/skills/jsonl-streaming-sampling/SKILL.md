---
name: jsonl-streaming-sampling
description: "Stream multi-hundred-MB .jsonl.gz review dumps and make a small, reproducible sample. Use when touching scripts/prepare_data.py or reading data/sample/."
user-invocable: false
metadata:
  skill-id: S08
  shared-by: "data-engineer, build-pipeline-engineer"
---

# Large-file streaming & sampling (.jsonl.gz) (S08)

Shared by: `data-engineer`, `build-pipeline-engineer`. Matrix: `docs/expert-roster.md` §3.

- `gzip.open(path, "rt", encoding="utf-8")` plus `json.loads(line)` per line. Never load the whole file into memory.
- Two passes: count reviews per `parent_asin`, then keep the chosen products' reviews (top 300 by count + 50 random long-tail, up to 100 reviews each).
- Reproducibility: `rng = random.Random(42)`. Record the seed, Python version, URLs and counts in `data/sample/DATACARD.md`.
- Real field names: `timestamp` (Unix **ms**), `helpful_vote`, `parent_asin`. `price` and `bought_together` may be `null`.
- Run locally only. Never run it during the Netlify build.
Details: `knowledge/data-engineer/streaming-and-sampling.md`, `knowledge/data-engineer/amazon-reviews-2023.md`.
