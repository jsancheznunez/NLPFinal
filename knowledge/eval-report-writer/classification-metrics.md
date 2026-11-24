# Classification metrics (scikit-learn)

Sources:
- https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html
- https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html
- https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html
- https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html

scikit-learn is an **evaluation-only** dependency. Put it in `requirements-dev.txt`, not the Netlify build.

- `classification_report(y_true, y_pred, *, labels=None, target_names=None, sample_weight=None, digits=2, output_dict=False, zero_division='warn')` gives a "Text summary of the precision, recall, F1 score for each class", plus macro and weighted averages. Use `output_dict=True` to save it as JSON (values are then not rounded). Set `labels=["negative","neutral","positive"]` for a fixed order and `zero_division=0` to avoid warnings.
- `confusion_matrix(y_true, y_pred, *, labels=None, sample_weight=None, normalize=None)`: "C_{i,j} is equal to the number of observations known to be in group i and predicted to be in group j." So rows are true labels and columns are predictions. `normalize='true'|'pred'|'all'`.
- `f1_score(..., average=...)`:
  - `'macro'`: "Calculate metrics for each label, and find their unweighted mean. This does not take label imbalance into account."
  - `'weighted'`: "average weighted by support... it can result in an F-score that is not between precision and recall."
  - `'micro'`: "Calculate metrics globally by counting the total true positives, false negatives and false positives."
  - **Report macro-F1 as the headline number.** Reviews are mostly positive, so accuracy and micro-F1 overstate performance.
- `cohen_kappa_score(y1, y2, *, labels=None, weights=None, ...)`: "a statistic that measures inter-annotator agreement." Use it for agreement between two human labelers on the hand-labeled aspect set. `weights='linear'|'quadratic'` suits ordinal labels, such as 1–5 stars compared with a binned compound score.
