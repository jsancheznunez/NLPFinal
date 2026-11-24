"use strict";
(async function dashboard() {
  const root = document.getElementById("dashboard");
  try {
    const [summary, productsDoc] = await Promise.all([loadJSON("data/summary.json"), loadJSON("data/products.json")]);
    const products = productsDoc.products;
    const byAsin = Object.fromEntries(products.map((p) => [p.parent_asin, p]));
    const ds = summary.dataset;
    const nl = summary.nltk;

    document.getElementById("dataset-line").textContent =
      `${fmt.int(ds.n_reviews)} reviews of ${fmt.int(ds.n_products)} products, ${ds.name}, category ${ds.category}, data as of ${ds.data_as_of}.`;

    // KPIs
    const kpis = el("div", { class: "kpis" },
      kpi(fmt.int(ds.n_products), "products (sample)"),
      kpi(fmt.int(ds.n_reviews), "reviews (sample)"),
      kpi(fmt.signed(nl.mean_compound), "mean VADER compound"),
      kpi(fmt.pct(nl.sentiment_mix.positive), "positive reviews"),
      kpi(fmt.pct(nl.sentiment_mix.negative), "negative reviews"),
      kpi(fmt.int(summary.aspects.n_pairs), "aspect-opinion pairs"));
    root.append(el("section", { class: "panel", "data-source": "metrics" },
      el("h2", {}, el("span", {}, "At a glance"), " ", badge("metrics"), badge("nltk"), badge("spacy+nltk")), kpis));

    const grid = el("div", { class: "grid two" });
    root.append(grid);

    // Best-seller proxy
    const best = summary.metrics.best_sellers.map((a) => byAsin[a]).filter(Boolean);
    grid.append(panel("metrics", "Best-seller proxy: most-rated products",
      el("p", { class: "muted" }, "Ranked by rating_number (number of ratings on the product page). This is a sales proxy, not sales."),
      chart({
        type: "bar",
        labels: best.map((p) => truncate(p.title, 38)),
        datasets: [{ label: "Ratings (rating_number)", data: best.map((p) => p.metrics.rating_number), backgroundColor: COLORS.metrics }],
        ariaLabel: `Best-seller proxy: ${truncate(best[0].title, 50)} leads with ${fmt.int(best[0].metrics.rating_number)} ratings.`,
        options: { indexAxis: "y", plugins: { legend: { display: false } } },
        height: 440,
        tableHeaders: ["Product", "Ratings", "Best-seller rank"],
        tableRows: best.map((p) => [p.title, fmt.int(p.metrics.rating_number), String(p.metrics.best_seller_rank)]),
      })));

    // Performance score
    const top = summary.metrics.top_performers.map((a) => byAsin[a]).filter(Boolean);
    const w = summary.metrics.weights;
    grid.append(panel("metrics", "Performance score: top 15",
      el("p", { class: "muted" },
        `Weights: popularity ${w.popularity}, adjusted rating ${w.adj_rating}, sentiment ${w.sentiment}, velocity ${w.velocity} (z-scores). `,
        el("a", { href: "how-it-works.html#score" }, "How the score works")),
      chart({
        type: "bar",
        labels: top.map((p) => truncate(p.title, 38)),
        datasets: [{ label: "Performance score", data: top.map((p) => p.metrics.score), backgroundColor: COLORS.metrics }],
        ariaLabel: `Top performer: ${truncate(top[0].title, 50)} with score ${fmt.num(top[0].metrics.score)}.`,
        options: { indexAxis: "y", plugins: { legend: { display: false } } },
        height: 440,
        tableHeaders: ["Rank", "Product", "Score", "Adj. rating", "Mean VADER"],
        tableRows: top.map((p) => [String(p.metrics.rank), p.title, fmt.num(p.metrics.score), fmt.num(p.metrics.adj_rating), fmt.signed(p.nltk.mean_compound)]),
      })));

    // Sentiment mix
    const mix = nl.sentiment_mix;
    grid.append(panel("nltk", "Review sentiment (VADER)",
      el("p", { class: "muted" }, "VADER compound per review: positive ≥ 0.05, negative ≤ −0.05, otherwise neutral."),
      chart({
        type: "doughnut",
        labels: ["Positive", "Neutral", "Negative"],
        datasets: [{ label: "Share of reviews", data: [mix.positive, mix.neutral, mix.negative].map((x) => +(100 * x).toFixed(1)),
          backgroundColor: [COLORS.positive, COLORS.neutral, COLORS.negative] }],
        ariaLabel: `Sentiment mix: ${fmt.pct(mix.positive)} positive, ${fmt.pct(mix.neutral)} neutral, ${fmt.pct(mix.negative)} negative.`,
        height: 260,
        tableHeaders: ["Sentiment", "% of reviews"],
        tableRows: [["Positive", fmt.pct(mix.positive, 1)], ["Neutral", fmt.pct(mix.neutral, 1)], ["Negative", fmt.pct(mix.negative, 1)]],
      })));

    // Aspects
    const asp = summary.aspects;
    grid.append(panel("spacy+nltk", "Aspects: complaints and selling points",
      el("p", { class: "muted" }, "spaCy extracts (aspect, opinion) pairs from the dependency parse; NLTK VADER scores each opinion."),
      el("div", { class: "grid" },
        el("div", {}, el("h3", {}, "Most complained-about"), aspectList(asp.top_negative.slice(0, 6), true)),
        el("div", {}, el("h3", {}, "Strongest selling points"), aspectList(asp.top_positive.slice(0, 6), false))),
      el("p", {}, el("a", { href: "aspects.html" }, "All aspects →"))));

    // Top terms
    grid.append(panel("nltk", "Top words by sentiment (FreqDist)",
      el("p", { class: "muted" }, "NLTK FreqDist over spaCy lemmas, ecommerce stopwords removed (negations kept for phrases)."),
      el("div", { class: "grid" },
        el("div", {}, el("h3", {}, "In positive reviews"), termList(nl.top_terms.positive.slice(0, 12))),
        el("div", {}, el("h3", {}, "In negative reviews"), termList(nl.top_terms.negative.slice(0, 12))))));

    // Collocations
    grid.append(panel("nltk", "Key phrases (collocations)",
      el("p", { class: "muted" }, `Bigram collocations ranked by ${nl.collocations.measure.replace("_", " ")}, frequency ≥ ${nl.collocations.min_freq}.`),
      el("div", { class: "grid" },
        el("div", {}, el("h3", {}, "Selling points"), termList(nl.collocations.positive.slice(0, 10), "phrase")),
        el("div", {}, el("h3", {}, "Complaint themes"), termList(nl.collocations.negative.slice(0, 10), "phrase")))));

    // Entities
    const sp = summary.spacy;
    grid.append(panel("spacy", "Brands and entities (NER)",
      el("p", { class: "muted" }, `${sp.model} NER plus an EntityRuler (before "ner") seeded with store names (BRAND) and title heads (PRODUCT).`),
      el("div", { class: "grid" },
        el("div", {}, el("h3", {}, "Brands mentioned"), termList(sp.top_brands.slice(0, 10), "text")),
        el("div", {}, el("h3", {}, "Other entities"), termList(sp.top_entities.slice(0, 10).map((e) => ({ text: `${e.text} (${e.label})`, count: e.count })), "text")))));

    // Opportunities
    const opps = summary.metrics.opportunities;
    const groups = {};
    for (const o of opps) (groups[o.flag] = groups[o.flag] || []).push(o);
    const oppBody = Object.keys(FLAG_TEXT).filter((f) => groups[f]).map((f) => el("div", {},
      el("h3", {}, `${FLAG_TEXT[f]} (${groups[f].length})`),
      el("ul", {}, groups[f].slice(0, 5).map((o) => el("li", {}, productLink(byAsin[o.parent_asin], 60), el("br"), el("span", { class: "muted" }, o.reason))))));
    root.append(panel("metrics", "Opportunities", el("p", { class: "muted" },
      "Rules over the proxy metrics, VADER sentiment and spaCy aspects. See How it works for the definitions."),
      el("div", { class: "grid" }, oppBody)));
  } catch (err) {
    showError(root, err);
  }

  function kpi(v, k) {
    return el("div", { class: "kpi" }, el("div", { class: "v" }, v), el("div", { class: "k" }, k));
  }
  function aspectList(items, neg) {
    if (!items.length) return el("p", { class: "muted" }, "None found.");
    return el("ul", {}, items.map((a) => el("li", {},
      el("strong", {}, a.aspect), ` (${a.mentions}) `,
      neg ? el("span", { class: "chip chip-negative" }, `− ${fmt.pct(a.pct_negative)} negative`) : sentimentChip(a.mean_compound),
      el("br"), el("span", { class: "muted" }, a.top_opinions.slice(0, 3).map((o) => `"${o.text}"`).join(", ")))));
  }
})();
