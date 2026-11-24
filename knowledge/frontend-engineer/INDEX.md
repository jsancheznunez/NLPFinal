# Knowledge: frontend-engineer

| File | Covers | Main sources |
|---|---|---|
| [static-data-loading.md](static-data-loading.md) | `fetch` for static JSON, error handling, no backend | developer.mozilla.org Fetch API "Using Fetch" |
| [charts-chartjs.md](charts-chartjs.md) | Chart.js setup from CDN, responsive containers, canvas accessibility | chartjs.org docs: getting-started, responsive, accessibility |
| [accessibility.md](accessibility.md) | WCAG 2.2 contrast (1.4.3, 1.4.11), responsive layout basics | w3.org/WAI/WCAG22/Understanding, MDN Responsive Design |

Hard limits: the site is static. There is no backend and no runtime Python. Data comes only from `site/data/*.json`, which build-pipeline-engineer writes against solution-architect's schemas.
