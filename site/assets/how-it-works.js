"use strict";
(async function howItWorks() {
  const list = document.getElementById("displacy-list");
  try {
    const doc = await loadJSON("displacy/sentences.json");
    list.replaceChildren(...doc.sentences.map((s, i) => el("figure", { class: "displacy-figure" },
      el("img", { src: `displacy/dep-${i + 1}.svg`, alt: `spaCy dependency parse of: ${s}`, loading: "lazy" }),
      el("figcaption", {}, `${i + 1}. "${s}" (${doc.model}, compact view with lemmas)`))));
  } catch (err) {
    showError(list, err);
  }
  const info = document.getElementById("build-info");
  try {
    const b = await loadJSON("data/build_info.json");
    info.replaceChildren(
      table(["Item", "Value"], [
        ["Context", b.context], ["Commit", b.commit_ref || "local build"], ["Python", b.python],
        ["NLTK", b.versions.nltk], ["spaCy", b.versions.spacy], ["Model", b.versions.en_core_web_sm],
        ["pandas", b.versions.pandas], ["Sample", `${fmt.int(b.sample.n_reviews)} reviews, ${b.sample.n_products} products`],
        ["Total build time", `${b.total_seconds.toFixed(1)} s (budget ${b.budget_seconds} s)`],
      ]),
      el("h3", {}, "Stage timings"),
      table(["Stage", "Seconds"], Object.entries(b.timings).map(([k, v]) => [k, v.toFixed(2)])));
  } catch (err) {
    showError(info, err);
  }
})();
