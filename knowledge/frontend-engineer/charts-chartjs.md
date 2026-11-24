# Charts with Chart.js

Sources:
- https://www.chartjs.org/docs/latest/getting-started/
- https://www.chartjs.org/docs/latest/configuration/responsive.html
- https://www.chartjs.org/docs/latest/general/accessibility.html
- npm registry (Nov 2026): latest `chart.js` is 4.6.2. **Pin an exact, well-established version**, e.g. `https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js` (checked: HTTP 200). The docs' unpinned `https://cdn.jsdelivr.net/npm/chart.js` must not be used.

## Getting started (docs)
```html
<div><canvas id="myChart"></canvas></div>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js"></script>
<script>
  new Chart(document.getElementById('myChart'), {
    type: 'bar',
    data: { labels: [...], datasets: [{ label: '# of Votes', data: [...], borderWidth: 1 }] },
    options: { scales: { y: { beginAtZero: true } } }
  });
</script>
```

## Responsive charts (docs)
- The canvas *render* size can't use relative units. These **don't work**: `<canvas height="40vh">`, `<canvas style="height:40vh">` (blurry), `<canvas style="margin:0 auto">` (it keeps shrinking).
- "Chart.js uses its parent container to update the canvas render and display sizes. However, this method requires the container to be **relatively positioned** and **dedicated to the chart canvas only**."
  ```html
  <div class="chart-container" style="position: relative; height:40vh; width:80vw"><canvas id="chart"></canvas></div>
  ```
- Options: `responsive` (default `true`), `maintainAspectRatio` (default `true`; set it to `false` when the container sets the height), `aspectRatio`, `onResize`, `resizeDelay`.

## Accessibility (docs)
- "the `canvas` content will not be accessible to screen readers." Accessibility "has to be added with ARIA attributes on the `canvas` element or added using internal fallback content."
- Good: `<canvas role="img" aria-label="Top 10 products by performance score">`, or meaningful fallback content inside `<canvas>…</canvas>`.
- Bad: no role or label, or fallback text like "Your browser does not support the canvas element."
- **Project rule:** every chart has `role="img"`, an `aria-label` that states the key takeaway, and a visible `<table>` or `<details>` with the same numbers.

## Chart map for the analyzer
| View | Chart |
|---|---|
| Best-sellers | horizontal bar: popularity proxy, top 15 |
| Performance | horizontal bar of the score, with a weights legend |
| Sentiment mix | stacked bar: % pos / neu / neg per product |
| Aspects | diverging bar: mean aspect sentiment (−1…+1), labeled with mention counts |
| Trends | line: reviews per month, plus a line of mean compound |
| Terms | bar: top FreqDist terms, split by sentiment |
