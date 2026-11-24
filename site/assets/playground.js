"use strict";
// "Analyze your own review": talks to the Pyodide module worker with an id-tagged request/response protocol.
(function playground() {
  const form = document.getElementById("analyze-form");
  const input = document.getElementById("review-input");
  const button = document.getElementById("analyze-button");
  const statusEl = document.getElementById("py-status");
  const out = document.getElementById("results");
  const examplesBox = document.getElementById("examples");

  let worker;
  let nextId = 1;
  const pending = new Map();
  let examples = [];
  let isReady = false;

  function setStatus(text) {
    statusEl.textContent = text;
  }

  try {
    worker = new Worker("assets/pyodide-worker.mjs", { type: "module" });
  } catch (err) {
    setStatus(`Your browser could not start a module Web Worker: ${err.message}`);
    return;
  }
  worker.onerror = (e) => setStatus(`Worker error: ${e.message || "failed to load"}`);
  worker.onmessage = (event) => {
    const msg = event.data;
    if (msg.type === "status") setStatus(`${msg.detail}…`);
    else if (msg.type === "ready") {
      isReady = true;
      document.body.dataset.pyodide = "ready";
      setStatus(`Ready: Pyodide ${msg.info.pyodide}, Python ${msg.info.python}, NLTK ${msg.info.nltk} (loaded in ${msg.info.seconds}s). Runs entirely in your browser.`);
    } else if (msg.type === "fatal") {
      setStatus(`Could not load Pyodide/NLTK: ${msg.error}`);
      button.disabled = false;
    } else if (msg.type === "result") {
      const p = pending.get(msg.id);
      if (!p) return;
      pending.delete(msg.id);
      msg.error ? p.reject(new Error(msg.error)) : p.resolve(msg.result);
    }
  };

  function analyze(text) {
    const id = nextId++;
    return new Promise((resolve, reject) => {
      pending.set(id, { resolve, reject });
      worker.postMessage({ id, text });
    });
  }

  async function run(text, buildResult) {
    if (!text.trim()) {
      setStatus("Type or paste a review first.");
      return;
    }
    button.disabled = true;
    out.replaceChildren(el("p", { class: "status" }, "Analyzing…"));
    if (!isReady) setStatus("Still loading Python and NLTK; your review will be analyzed as soon as they are ready…");
    try {
      const t0 = performance.now();
      const r = await analyze(text);
      render(r, buildResult, ((performance.now() - t0) / 1000).toFixed(2));
    } catch (err) {
      out.replaceChildren(el("p", { class: "error", role: "alert" }, err.message));
    } finally {
      button.disabled = false;
    }
  }

  function render(r, buildResult, secs) {
    const s = r.sentiment;
    const parts = [];
    const sentimentPanel = panel("nltk", "Sentiment (VADER)",
      el("div", { class: "kpis" },
        kpi(el("span", { id: "out-compound", "data-compound": String(s.compound) }, fmt.signed(s.compound, 4)), "compound"),
        kpi(el("span", { id: "out-label" }, s.label), "label (±0.05)"),
        kpi(fmt.num(s.pos, 3), "pos"), kpi(fmt.num(s.neu, 3), "neu"), kpi(fmt.num(s.neg, 3), "neg")),
      el("p", { class: "muted" }, `Analyzed ${r.n_chars} characters, ${r.n_tokens} tokens in ${secs}s with NLTK ${r.nltk_version} in your browser.`));
    if (buildResult) {
      const diff = Math.abs(buildResult.sentiment.compound - s.compound);
      sentimentPanel.append(el("p", { id: "parity", "data-diff": String(diff) },
        diff <= 1e-4
          ? el("span", { class: "chip chip-positive" }, `Matches the build-time score (${fmt.signed(buildResult.sentiment.compound, 4)})`)
          : el("span", { class: "chip chip-negative" }, `Differs from the build-time score ${fmt.signed(buildResult.sentiment.compound, 4)} by ${diff.toFixed(4)}`)));
    }
    parts.push(sentimentPanel);
    parts.push(panel("nltk", "Sentences (Punkt + VADER)",
      r.sentences.length ? table(["Sentence", "Compound", "Label"], r.sentences.map((x) => [x.text, fmt.signed(x.compound, 4), sentimentChip(x.compound)]))
        : el("p", { class: "muted" }, "No sentences.")));
    parts.push(panel("nltk", "Top words (FreqDist)", termList(r.top_words)));
    parts.push(panel("nltk", "Key phrases (collocations)",
      el("p", { class: "muted" }, `Bigrams ranked by ${r.key_phrases.measure.replace("_", " ")}, min frequency ${r.key_phrases.min_freq}.`),
      termList(r.key_phrases.items, "phrase")));
    parts.push(panel("nltk", "Tokens (TweetTokenizer)",
      el("div", { class: "tokens" }, r.tokens.map((t) => el("code", {}, t)))));
    out.replaceChildren(el("div", { class: "grid two" }, parts));
  }

  function kpi(v, k) {
    return el("div", { class: "kpi" }, el("div", { class: "v" }, v), el("div", { class: "k" }, k));
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = input.value;
    const match = examples.find((x) => x.text === text);
    run(text, match ? match.result : null);
  });

  loadJSON("data/nltk_examples.json").then((doc) => {
    examples = doc.items;
    examplesBox.replaceChildren(...examples.map((x) =>
      el("button", { type: "button", class: "secondary", "data-example": x.id, onclick: null }, x.id.replace(/-/g, " "))));
    examplesBox.querySelectorAll("button").forEach((b, i) => b.addEventListener("click", () => {
      input.value = examples[i].text;
      run(examples[i].text, examples[i].result);
    }));
  }).catch((err) => showError(examplesBox, err));
})();
