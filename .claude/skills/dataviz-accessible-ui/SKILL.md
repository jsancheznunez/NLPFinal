---
name: dataviz-accessible-ui
description: "Make charts and UI that are readable, accessible (WCAG 2.2 AA) and responsive. Use for any chart, color, layout or interaction decision."
user-invocable: false
metadata:
  skill-id: S23
  shared-by: "frontend-engineer, pyodide-engineer"
---

# Data visualization & accessible UI (S23)

Shared by: `frontend-engineer`, `pyodide-engineer`. Matrix: `docs/expert-roster.md` §3.

- Chart.js canvases: `role="img"` and an `aria-label` that states the takeaway, plus a data table or `<details>` alternative.
- Responsive charts: a dedicated `position: relative` container per canvas, and `maintainAspectRatio: false` when the container sets the height.
- Contrast: text 4.5:1 (large text 3:1); chart marks, focus rings and UI parts 3:1. No rounding (4.499 fails).
- Don't encode sentiment by color alone. Add +/− signs or labels. Use a diverging scale for aspect sentiment.
- Layout: viewport meta, 16px gutters, no horizontal scroll at 360px, keyboard-operable controls, and `aria-live="polite"` for playground results.
Details: `knowledge/frontend-engineer/charts-chartjs.md`, `knowledge/frontend-engineer/accessibility.md`.
