# Evaluating VADER (and aspects) for the report

Sources:
- https://github.com/cjhutto/vaderSentiment (README, "About the Scoring")
- https://www.nltk.org/howto/sentiment.html

## Label mapping
- Weak gold labels from stars: 1–2 → negative, 3 → neutral, 4–5 → positive. State that this is a proxy for true sentiment.
- VADER labels use the README thresholds: positive `compound >= 0.05`, neutral `-0.05 < compound < 0.05`, negative `compound <= -0.05`.

## What to report
1. Class distribution of stars. Expect a heavy skew toward positive.
2. `classification_report` (macro-F1 as the headline), a confusion matrix normalized by row, and Cohen's kappa (quadratic) between stars (1–5) and compound binned into 5.
3. Error analysis: 10 examples each of 5★ with negative compound, and 1★ with positive compound. Group them as sarcasm, domain terms ("runs small"), mixed "but" sentences, or wrong-star mistakes.
4. Aspect extraction: precision of (aspect, opinion, negated) triples on about 100 hand-labeled sentences, plus inter-annotator kappa if two people label.
5. Agreement between the browser and the build: the same 50 texts scored in Pyodide and in the build must match within 1e-4.

## Limitations to state
- The README says VADER is "specifically attuned to sentiments expressed in social media". It's lexicon-based (over 9,000 rated tokens) and handles negation, boosters, caps, punctuation, emoji and slang. It does **not** understand domain-specific phrases or sarcasm well.
- The NLTK note says hashtags are ignored ("#BAD is neutral").
- The "sales" metrics are proxies (rating counts and review velocity), not revenue.
- spaCy analysis runs at build time only. Live analysis in the browser uses NLTK alone.
