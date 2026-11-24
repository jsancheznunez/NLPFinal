# Accessibility and responsive layout

Sources:
- https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html (SC 1.4.3)
- https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html (SC 1.4.11)
- https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Responsive_Design

## Contrast
- **Text (1.4.3):** "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1." Exception: "Large-scale text... at least 3:1", where large means 18 point, or 14 point bold.
- "The 3:1 and 4.5:1 contrast ratios... are intended to be treated as threshold values... the computed values should not be rounded (e.g., 4.499:1 would not meet the 4.5:1 threshold)."
- **Non-text (1.4.11):** "User Interface Components" and "Graphical Objects: Parts of graphics required to understand the content" need "a contrast ratio of at least 3:1 against adjacent color(s)". This covers chart bars, lines, focus rings and sentiment color chips.
- Don't encode sentiment by color alone. Pair red and green with signs (+/−), labels or patterns.

## Responsive design (MDN)
- "HTML is fundamentally responsive, or fluid." Responsive design uses "fluid grids, fluid images, and media queries".
- Use `<meta name="viewport" content="width=device-width, initial-scale=1">`, CSS grid/flex with `minmax()`, `max-width: 100%` on media, and charts in dedicated relative containers (see charts-chartjs.md).

## Project checklist
- 16px minimum side gutter and no horizontal scroll at 360px width.
- Keyboard: every control is reachable with Tab, has a visible focus ring (3:1 contrast), and the playground's "Analyze" button works with Enter.
- Live regions: the playground result container has `aria-live="polite"` so screen readers announce new scores.
- displaCy colors (from spacy-expert) must meet 4.5:1 for the label text.
