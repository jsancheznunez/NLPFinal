# Knowledge: data-engineer

| File | Covers | Main sources |
|---|---|---|
| [amazon-reviews-2023.md](amazon-reviews-2023.md) | Dataset fields **verified against the real files**, download URLs, sizes, citation, license status | amazon-reviews-2023.github.io, HF dataset card, arXiv 2403.03952, live file check |
| [streaming-and-sampling.md](streaming-and-sampling.md) | `gzip.open` text mode, `json`, `random` reproducibility, pandas `read_json(lines=True, chunksize=…)` | docs.python.org (gzip, json, random), pandas.pydata.org read_json |

Project context: [docs/03-dataset.md](../../docs/03-dataset.md). Your output (`data/sample/`) feeds nltk-expert, spacy-expert and metrics-engineer.
