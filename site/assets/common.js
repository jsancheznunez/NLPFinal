// Shared helpers for every page. No backend: data comes only from site/data/*.json
// (written at build time by scripts/build_analysis.py against schemas/*.schema.json).
"use strict";

const SOURCE_LABELS = {
  nltk: "NLTK",
  spacy: "spaCy",
  "spacy+nltk": "spaCy + NLTK",
  metrics: "Metrics (proxy)",
};

const COLORS = {
  positive: "#1b7f3b",
  neutral: "#6b6f76",
  negative: "#b3261e",
  nltk: "#0b5cad",
  spacy: "#00708f",
  metrics: "#5b3fa8",
};

/** MDN "Using Fetch" pattern: check response.ok, show a visible error instead of a blank panel. */
async function loadJSON(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Couldn't load ${path} (HTTP ${response.status})`);
  }
  return response.json();
}

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else node.setAttribute(k, v === true ? "" : v);
  }
  for (const c of children.flat()) {
    if (c === null || c === undefined) continue;
    node.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return node;
}

function badge(source) {
  const cls = source === "spacy+nltk" ? "badge badge-spacy-nltk" : `badge badge-${source.replace(/[^a-z]/g, "")}`;
  return el("span", { class: cls, "data-badge": source, title: `Produced by ${SOURCE_LABELS[source]}` }, SOURCE_LABELS[source]);
}

/** A labelled result panel: <section class="panel" data-source="nltk"><h2>Title <badge></h2>... */
function panel(source, title, ...body) {
  return el("section", { class: "panel", "data-source": source },
    el("h2", {}, el("span", {}, title), " ", badge(source)),
    ...body);
}

function showError(target, err) {
  const box = typeof target === "string" ? document.querySelector(target) : target;
  if (box) box.replaceChildren(el("p", { class: "error", role: "alert" }, String(err.message || err)));
  console.warn(err);
}

const fmt = {
  num: (x, d = 2) => (x === null || x === undefined ? "n/a" : Number(x).toFixed(d)),
  int: (x) => (x === null || x === undefined ? "n/a" : Number(x).toLocaleString("en-US")),
  pct: (x, d = 0) => (x === null || x === undefined ? "n/a" : `${(100 * x).toFixed(d)}%`),
  signed: (x, d = 2) => (x === null || x === undefined ? "n/a" : `${x >= 0 ? "+" : "−"}${Math.abs(x).toFixed(d)}`),
  money: (x) => (x === null || x === undefined ? "n/a" : `$${Number(x).toFixed(2)}`),
};

function sentimentChip(compound) {
  const label = compound >= 0.05 ? "positive" : compound <= -0.05 ? "negative" : "neutral";
  const sign = label === "positive" ? "+" : label === "negative" ? "−" : "±";
  return el("span", { class: `chip chip-${label}` }, `${sign} ${label} (${fmt.signed(compound)})`);
}

function table(headers, rows, caption) {
  return el("table", { class: "data" },
    caption ? el("caption", {}, caption) : null,
    el("thead", {}, el("tr", {}, headers.map((h) => el("th", { scope: "col" }, h)))),
    el("tbody", {}, rows.map((r) => el("tr", {}, r.map((c) => el("td", {}, c))))));
}

/**
 * Accessible Chart.js chart: canvas with role="img" + aria-label (the takeaway),
 * in a relatively positioned container dedicated to the canvas, plus a <details> data table.
 */
function chart({ type, labels, datasets, ariaLabel, options = {}, height = 320, tableHeaders, tableRows }) {
  const canvas = el("canvas", { role: "img", "aria-label": ariaLabel });
  canvas.append(el("p", {}, ariaLabel));
  const box = el("div", { class: "chart-box", style: `height:${height}px` }, canvas);
  const headers = tableHeaders || ["Label", ...datasets.map((d) => d.label)];
  const rows = tableRows || labels.map((l, i) => [l, ...datasets.map((d) => String(d.data[i]))]);
  const details = el("details", { class: "chart-table" }, el("summary", {}, "Show data table"), table(headers, rows));
  const fig = el("figure", { class: "chart" }, box, details);
  requestAnimationFrame(() => {
    if (typeof Chart === "undefined") {
      box.replaceChildren(el("p", { class: "error" }, "Chart.js failed to load. See the data table below."));
      details.open = true;
      return;
    }
    new Chart(canvas, {
      type,
      data: { labels, datasets },
      options: Object.assign({ responsive: true, maintainAspectRatio: false, animation: false }, options),
    });
  });
  return fig;
}

function truncate(s, n = 60) {
  return s.length > n ? `${s.slice(0, n - 1)}…` : s;
}

function productLink(p, n = 70) {
  return el("a", { href: `product.html?asin=${encodeURIComponent(p.parent_asin)}` }, truncate(p.title, n));
}

function termList(items, key = "term") {
  if (!items || !items.length) return el("p", { class: "muted" }, "Not enough text.");
  return el("ol", { class: "terms" }, items.map((t) =>
    el("li", {}, el("span", { class: "term" }, t[key]), el("span", { class: "count" }, ` ${t.count}`))));
}

const FLAG_TEXT = {
  fix_top_complaint: "Fix the top complaint",
  under_marketed_gem: "Under-marketed gem",
  trending: "Trending",
  price_value_mismatch: "Price/value mismatch",
};

function flagChips(flags) {
  return flags.map((f) => el("span", { class: `flag flag-${f}` }, FLAG_TEXT[f] || f));
}

// Mark the current page in the header nav.
document.addEventListener("DOMContentLoaded", () => {
  const here = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".site-nav a").forEach((a) => {
    if (a.getAttribute("href") === here) a.setAttribute("aria-current", "page");
  });
});
