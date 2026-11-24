"use strict";
(async function productPage() {
  const root = document.getElementById("product");
  const asin = new URLSearchParams(location.search).get("asin");
  try {
    let a = asin;
    if (!a || !/^[A-Z0-9]{10}$/.test(a)) {
      const doc = await loadJSON("data/products.json");
      a = doc.products[0].parent_asin;  // default: the top-ranked product
    }
    const p = await loadJSON(`data/product/${a}.json`);
    document.title = `${truncate(p.title, 50)} | Product Performance Analyzer`;
    document.getElementById("product-title").textContent = p.title;
    document.getElementById("product-sub").textContent =
      `${p.store || "Unknown store"} · ASIN ${p.parent_asin} · price ${fmt.money(p.price)}`;

    const m = p.metrics, n = p.nltk, s = p.spacy, asp = p.aspects;
    const grid = el("div", { class: "grid two" });
    root.append(grid);

    // Metrics overview
    grid.append(panel("metrics", "Performance (proxies)",
      el("div", { class: "kpis" },
        kpi(`#${m.rank}`, "performance rank"), kpi(fmt.num(m.score), "score"),
        kpi(`#${m.best_seller_rank}`, "best-seller proxy rank"), kpi(fmt.int(m.rating_number), "ratings (rating_number)"),
        kpi(fmt.num(m.adj_rating), "Bayesian rating (m=20)"), kpi(`${fmt.num(m.velocity)}×`, "review velocity (6 mo)"),
        kpi(m.price_band, "price band"), kpi(fmt.int(m.n_reviews), "reviews in sample")),
      m.flags.length ? el("p", {}, flagChips(m.flags)) : null,
      chart({
        type: "bar", labels: ["1★", "2★", "3★", "4★", "5★"],
        datasets: [{ label: "Reviews", data: [1, 2, 3, 4, 5].map((k) => m.rating_histogram[String(k)]), backgroundColor: COLORS.metrics }],
        ariaLabel: `Star ratings in the sample: ${[1, 2, 3, 4, 5].map((k) => `${k} star ${m.rating_histogram[String(k)]}`).join(", ")}.`,
        options: { plugins: { legend: { display: false } } }, height: 200,
      })));

    // NLTK sentiment
    const mix = n.sentiment_mix;
    const monthly = n.monthly_sentiment.filter((x) => x.n_reviews > 0);
    grid.append(panel("nltk", "Sentiment (VADER)",
      el("p", {}, "Mean compound ", sentimentChip(n.mean_compound), ` · ${fmt.pct(mix.positive)} positive, ${fmt.pct(mix.neutral)} neutral, ${fmt.pct(mix.negative)} negative`),
      monthly.length ? chart({
        type: "line", labels: monthly.map((x) => x.month),
        datasets: [{ label: "Mean VADER compound", data: monthly.map((x) => x.mean_compound), borderColor: COLORS.nltk, backgroundColor: COLORS.nltk }],
        ariaLabel: `Monthly mean VADER compound over the last 24 months, ${monthly.length} months with reviews.`,
        options: { scales: { y: { min: -1, max: 1 } } }, height: 220,
        tableHeaders: ["Month", "Reviews", "Mean compound"], tableRows: monthly.map((x) => [x.month, String(x.n_reviews), fmt.signed(x.mean_compound)]),
      }) : el("p", { class: "muted" }, "No reviews in the last 24 months of the sample."),
      el("h3", {}, "Most helpful reviews"),
      exampleBlock("Positive", n.examples.most_helpful_positive),
      exampleBlock("Negative", n.examples.most_helpful_negative)));

    // Aspects
    const items = asp.items.slice(0, 12);
    grid.append(panel("spacy+nltk", "Aspect sentiment",
      el("p", { class: "muted" }, `${asp.n_pairs} (aspect, opinion) pairs from the spaCy dependency parse, each scored with VADER.`),
      items.length ? chart({
        type: "bar", labels: items.map((x) => `${x.aspect} (${x.mentions})`),
        datasets: [{ label: "Mean VADER compound", data: items.map((x) => x.mean_compound),
          backgroundColor: items.map((x) => (x.mean_compound >= 0.05 ? COLORS.positive : x.mean_compound <= -0.05 ? COLORS.negative : COLORS.neutral)) }],
        ariaLabel: `Aspect sentiment for the ${items.length} most-mentioned aspects; ${items[0].aspect} is mentioned most (${items[0].mentions}).`,
        options: { indexAxis: "y", scales: { x: { min: -1, max: 1 } }, plugins: { legend: { display: false } } }, height: 60 + 26 * items.length,
        tableHeaders: ["Aspect", "Mentions", "Mean compound", "% negative", "Top opinions"],
        tableRows: items.map((x) => [x.aspect, String(x.mentions), fmt.signed(x.mean_compound), fmt.pct(x.pct_negative), x.top_opinions.map((o) => o.text).join(", ")]),
      }) : el("p", { class: "muted" }, "Not enough aspect mentions (need 2+ per aspect).")));

    // NLTK terms + collocations
    grid.append(panel("nltk", "Words and key phrases",
      el("div", { class: "grid" },
        el("div", {}, el("h3", {}, "Top words, positive reviews"), termList(n.top_terms.positive.slice(0, 10))),
        el("div", {}, el("h3", {}, "Top words, negative reviews"), termList(n.top_terms.negative.slice(0, 10))),
        el("div", {}, el("h3", {}, "Key phrases, positive"), termList(n.collocations.positive, "phrase")),
        el("div", {}, el("h3", {}, "Key phrases, negative"), termList(n.collocations.negative, "phrase"))),
      el("p", { class: "muted" }, `FreqDist and likelihood-ratio collocations (min frequency ${n.collocations.min_freq}) over spaCy lemmas.`)));

    // spaCy entities
    grid.append(panel("spacy", "Entities, brands and noun chunks",
      el("p", { class: "muted" }, `${s.n_entities} entities found by ${s.model} + EntityRuler.`),
      el("div", { class: "grid" },
        el("div", {}, el("h3", {}, "Brands (BRAND)"), termList(s.brands, "text")),
        el("div", {}, el("h3", {}, "Products (PRODUCT)"), termList(s.products, "text")),
        el("div", {}, el("h3", {}, "Other entities"), termList(s.entities.map((e) => ({ text: `${e.text} (${e.label})`, count: e.count })), "text")),
        el("div", {}, el("h3", {}, "Noun chunks"), termList(s.noun_chunks.slice(0, 10), "text")))));
  } catch (err) {
    showError(root, err);
  }

  function kpi(v, k) {
    return el("div", { class: "kpi" }, el("div", { class: "v" }, v), el("div", { class: "k" }, k));
  }
  function exampleBlock(label, ex) {
    if (!ex) return el("p", { class: "muted" }, `No ${label.toLowerCase()} review.`);
    return el("div", {}, el("strong", {}, `${label}: `), sentimentChip(ex.compound),
      ` ${ex.rating}★ · ${ex.helpful_vote} helpful votes · ${ex.date}`,
      el("blockquote", { class: "review" }, ex.text));
  }
})();
