"use strict";
(async function productsPage() {
  const root = document.getElementById("products");
  try {
    const doc = await loadJSON("data/products.json");
    const all = doc.products;
    const cols = [
      { key: "rank", label: "Rank", src: "metrics", get: (p) => p.metrics.rank, show: (p) => String(p.metrics.rank) },
      { key: "title", label: "Product", src: null, get: (p) => p.title.toLowerCase(), show: (p) => productLink(p, 70) },
      { key: "store", label: "Store", src: null, get: (p) => (p.store || "").toLowerCase(), show: (p) => p.store || "n/a" },
      { key: "score", label: "Score", src: "metrics", get: (p) => p.metrics.score, show: (p) => fmt.num(p.metrics.score) },
      { key: "ratings", label: "Ratings (proxy)", src: "metrics", get: (p) => p.metrics.rating_number ?? -1, show: (p) => fmt.int(p.metrics.rating_number) },
      { key: "adj", label: "Adj. rating", src: "metrics", get: (p) => p.metrics.adj_rating, show: (p) => fmt.num(p.metrics.adj_rating) },
      { key: "vader", label: "Mean VADER", src: "nltk", get: (p) => p.nltk.mean_compound, show: (p) => sentimentChip(p.nltk.mean_compound) },
      { key: "neg", label: "% negative", src: "nltk", get: (p) => p.nltk.pct_negative, show: (p) => fmt.pct(p.nltk.pct_negative) },
      { key: "complaint", label: "Top complaint", src: "spacy+nltk", get: (p) => (p.aspects.top_negative[0] || {}).aspect || "", show: (p) => (p.aspects.top_negative[0] || {}).aspect || "n/a" },
      { key: "flags", label: "Flags", src: "metrics", get: (p) => p.metrics.flags.length, show: (p) => el("span", {}, flagChips(p.metrics.flags)) },
    ];
    let sortKey = "rank";
    let asc = true;

    const search = el("input", { type: "search", id: "product-search", placeholder: "Search title or store", "aria-label": "Search products" });
    const flagSel = el("select", { id: "flag-filter", "aria-label": "Filter by opportunity flag" },
      el("option", { value: "" }, "All products"),
      Object.entries(FLAG_TEXT).map(([k, v]) => el("option", { value: k }, v)));
    const count = el("span", { class: "status", "aria-live": "polite" });
    const tbody = el("tbody");
    const thead = el("thead", {}, el("tr", {}, cols.map((c) => el("th", { scope: "col", "aria-sort": c.key === sortKey ? "ascending" : null },
      el("button", { class: "sort", type: "button", "data-key": c.key }, c.label), c.src ? el("br") : null, c.src ? badge(c.src) : null))));
    const tableEl = el("table", { class: "data", id: "products-table" }, thead, tbody);

    root.append(panel("metrics", "All products",
      el("p", { class: "muted" }, `Score weights: ${Object.entries(doc.weights).map(([k, v]) => `${k} ${v}`).join(", ")}. Ratings and velocity are sales proxies.`),
      el("div", { class: "controls" }, search, flagSel, count),
      el("div", { class: "table-scroll" }, tableEl)));

    function render() {
      const q = search.value.trim().toLowerCase();
      const f = flagSel.value;
      const col = cols.find((c) => c.key === sortKey);
      const rows = all.filter((p) => (!q || p.title.toLowerCase().includes(q) || (p.store || "").toLowerCase().includes(q))
        && (!f || p.metrics.flags.includes(f)));
      rows.sort((a, b) => {
        const x = col.get(a), y = col.get(b);
        const r = x < y ? -1 : x > y ? 1 : a.parent_asin.localeCompare(b.parent_asin);
        return asc ? r : -r;
      });
      tbody.replaceChildren(...rows.map((p) => el("tr", {}, cols.map((c) => el("td", {}, c.show(p))))));
      count.textContent = `${rows.length} of ${all.length} products`;
      thead.querySelectorAll("th").forEach((th, i) => {
        th.setAttribute("aria-sort", cols[i].key === sortKey ? (asc ? "ascending" : "descending") : "none");
      });
    }
    thead.addEventListener("click", (e) => {
      const b = e.target.closest("button.sort");
      if (!b) return;
      const k = b.dataset.key;
      if (k === sortKey) asc = !asc;
      else { sortKey = k; asc = k === "rank" || k === "title" || k === "store"; }
      render();
    });
    search.addEventListener("input", render);
    flagSel.addEventListener("change", render);
    const initial = new URLSearchParams(location.search).get("flag");
    if (initial) flagSel.value = initial;
    render();
  } catch (err) {
    showError(root, err);
  }
})();
