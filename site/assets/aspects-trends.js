"use strict";
// Used by aspects.html (data-page="aspects") and trends.html (data-page="trends").
(async function aspectsTrends() {
  const page = document.body.dataset.page;
  const root = document.getElementById(page);
  try {
    if (page === "aspects") await aspects(root);
    else await trends(root);
  } catch (err) {
    showError(root, err);
  }

  async function aspects(root) {
    const doc = await loadJSON("data/aspects.json");
    const items = doc.items;
    const top = items.slice(0, 25);
    root.append(panel("spacy+nltk", "Category aspect leaderboard",
      el("p", { class: "muted" }, doc.method),
      el("p", {}, `${fmt.int(doc.n_pairs)} pairs in total; aspects with 8+ mentions are shown.`),
      chart({
        type: "bar", labels: top.map((x) => `${x.aspect} (${x.mentions})`),
        datasets: [{ label: "Mean VADER compound", data: top.map((x) => x.mean_compound),
          backgroundColor: top.map((x) => (x.mean_compound >= 0.05 ? COLORS.positive : x.mean_compound <= -0.05 ? COLORS.negative : COLORS.neutral)) }],
        ariaLabel: `Mean sentiment of the 25 most-mentioned aspects; "${top[0].aspect}" is mentioned most (${top[0].mentions} times).`,
        options: { indexAxis: "y", scales: { x: { min: -1, max: 1 } }, plugins: { legend: { display: false } } },
        height: 60 + 24 * top.length,
        tableHeaders: ["Aspect", "Mentions", "Mean compound"],
        tableRows: top.map((x) => [x.aspect, String(x.mentions), fmt.signed(x.mean_compound)]),
      })));
    root.append(panel("spacy+nltk", "All aspects",
      el("div", { class: "table-scroll" }, table(
        ["Aspect", "Mentions", "Products", "Mean compound", "% negative", "Top opinions (spaCy)"],
        items.map((x) => [x.aspect, String(x.mentions), String(x.n_products), sentimentChip(x.mean_compound), fmt.pct(x.pct_negative),
          x.top_opinions.map((o) => `${o.text} (${o.count})`).join(", ")])))));
  }

  async function trends(root) {
    const doc = await loadJSON("data/trends.json");
    const m = doc.metrics.monthly;
    const s = doc.nltk.monthly_sentiment;
    root.append(panel("metrics", "Review volume per month (proxy)",
      el("p", { class: "muted" }, "Reviews per month in the sample, last 36 months. Review counts are a demand proxy, not sales."),
      chart({
        type: "line", labels: m.map((x) => x.month),
        datasets: [{ label: "Reviews", data: m.map((x) => x.n_reviews), borderColor: COLORS.metrics, backgroundColor: COLORS.metrics }],
        ariaLabel: `Monthly review counts over 36 months, peaking at ${Math.max(...m.map((x) => x.n_reviews))} reviews.`,
        height: 260,
        tableHeaders: ["Month", "Reviews", "Mean rating"], tableRows: m.map((x) => [x.month, String(x.n_reviews), fmt.num(x.mean_rating)]),
      })));
    const withData = s.filter((x) => x.n_reviews > 0);
    root.append(panel("nltk", "Sentiment per month (VADER)",
      chart({
        type: "line", labels: withData.map((x) => x.month),
        datasets: [
          { label: "Mean compound", data: withData.map((x) => x.mean_compound), borderColor: COLORS.nltk, backgroundColor: COLORS.nltk },
          { label: "% negative", data: withData.map((x) => x.pct_negative), borderColor: COLORS.negative, backgroundColor: COLORS.negative, borderDash: [6, 4] },
        ],
        ariaLabel: "Monthly mean VADER compound and share of negative reviews over the last 36 months.",
        options: { scales: { y: { min: -1, max: 1 } } }, height: 260,
        tableHeaders: ["Month", "Reviews", "Mean compound", "% negative"],
        tableRows: withData.map((x) => [x.month, String(x.n_reviews), fmt.signed(x.mean_compound), fmt.pct(x.pct_negative)]),
      })));
    const t = doc.nltk.trending_terms;
    root.append(panel("nltk", "Trending terms",
      el("p", { class: "muted" }, `Change in FreqDist relative frequency, ${doc.nltk.window}. Terms need 5+ recent mentions across 3+ products.`),
      t.length ? el("div", { class: "table-scroll" }, table(["Term", "Recent count", "Recent freq", "Previous freq", "Change"],
        t.map((x) => [x.term, String(x.recent_count), fmt.pct(x.recent_freq, 2), fmt.pct(x.previous_freq, 2), fmt.signed(100 * x.delta, 2) + " pp"])))
        : el("p", { class: "muted" }, "No trending terms in this window.")));
  }
})();
