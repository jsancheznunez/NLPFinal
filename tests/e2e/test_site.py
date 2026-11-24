"""End-to-end: every page renders real data, carries NLTK/spaCy labels and links to Resources;
the Pyodide playground returns VADER scores equal to the build's (within 1e-4).

    pytest tests/e2e --tracing off            # serves site/ on a free local port
"""
import json
import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e
SITE = Path(__file__).resolve().parents[2] / "site"
PAGES = ["index.html", "products.html", "product.html", "aspects.html", "trends.html",
         "playground.html", "how-it-works.html", "resources.html"]


@pytest.fixture
def console_errors(page: Page):
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    return errors


@pytest.mark.parametrize("name", PAGES)
def test_page_has_labels_and_resources_link(page: Page, site_server, name, console_errors):
    page.goto(f"{site_server}/{name}")
    expect(page.locator(".legend-badges [data-badge='nltk']")).to_have_text("NLTK")
    expect(page.locator(".legend-badges [data-badge='spacy']")).to_have_text("spaCy")
    expect(page.locator("header .site-nav a[href='resources.html']")).to_be_visible()
    expect(page.locator("footer a[href='resources.html']")).to_be_visible()
    page.wait_for_load_state("networkidle") if name != "playground.html" else None
    assert not [e for e in console_errors if "favicon" not in e], console_errors


def test_resources_link_works(page: Page, site_server):
    page.goto(f"{site_server}/index.html")
    page.locator("footer a[href='resources.html']").click()
    expect(page).to_have_url(re.compile(r"resources\.html$"))
    expect(page.get_by_role("heading", name="Resources", exact=True)).to_be_visible()
    for href in ["https://github.com/jsancheznunez/NLPFinal",
                 "https://github.com/jsancheznunez/NLPFinal/blob/main/docs/GUIDE.md",
                 "https://arxiv.org/abs/2403.03952", "https://amazon-reviews-2023.github.io/",
                 "https://www.nltk.org/", "https://github.com/cjhutto/vaderSentiment", "https://spacy.io/models/en",
                 "https://pyodide.org/en/stable/usage/webworker.html", "https://pandas.pydata.org/docs/user_guide/groupby.html",
                 "https://www.chartjs.org/docs/latest/getting-started/", "https://json-schema.org/learn/getting-started-step-by-step",
                 "https://docs.pytest.org/en/stable/getting-started.html", "https://playwright.dev/python/docs/intro",
                 "https://docs.netlify.com/build/configure-builds/file-based-configuration/"]:
        expect(page.locator(f"a[href='{href}']").first).to_be_attached()


def test_dashboard_renders_real_data(page: Page, site_server, console_errors):
    summary = json.loads((SITE / "data" / "summary.json").read_text())
    page.goto(f"{site_server}/index.html")
    expect(page.locator("#dataset-line")).to_contain_text(f"{summary['dataset']['n_reviews']:,}")
    for src in ["metrics", "nltk", "spacy", "spacy+nltk"]:
        expect(page.locator(f"#dashboard section.panel[data-source='{src}']").first).to_be_visible()
        expect(page.locator(f"#dashboard section.panel[data-source='{src}'] h2 .badge").first).to_be_visible()
    canvases = page.locator("#dashboard canvas")
    assert canvases.count() >= 3
    for i in range(canvases.count()):
        c = canvases.nth(i)
        assert c.get_attribute("role") == "img" and c.get_attribute("aria-label")
    expect(page.locator("#dashboard details.chart-table").first).to_be_attached()
    page.wait_for_load_state("networkidle")
    assert not console_errors


def test_product_page_and_table(page: Page, site_server, console_errors):
    page.goto(f"{site_server}/products.html")
    rows = page.locator("#products-table tbody tr")
    expect(rows).to_have_count(200)
    page.fill("#product-search", "zzzz-no-such-product")
    expect(rows).to_have_count(0)
    page.fill("#product-search", "")
    page.locator("#products-table tbody tr a").first.click()
    expect(page).to_have_url(re.compile(r"product\.html\?asin=[A-Z0-9]{10}$"))
    for src in ["metrics", "nltk", "spacy", "spacy+nltk"]:
        expect(page.locator(f"#product section.panel[data-source='{src}']").first).to_be_visible()
    assert not console_errors


def test_how_it_works_shows_displacy(page: Page, site_server):
    page.goto(f"{site_server}/how-it-works.html")
    img = page.locator("#displacy-list img").first
    expect(img).to_be_visible()
    assert page.evaluate("(img) => img.naturalWidth > 0", img.element_handle())
    expect(page.locator("#build-info table").first).to_contain_text("3.9.4")


def test_no_horizontal_scroll_at_360px(page: Page, site_server):
    page.set_viewport_size({"width": 360, "height": 800})
    for name in ["index.html", "resources.html", "playground.html"]:
        page.goto(f"{site_server}/{name}")
        page.wait_for_timeout(500)
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"), name


def test_playground_matches_build_scores(page: Page, site_server, console_errors):
    """Pyodide 314.0.8 + nltk 3.9.4 in a module worker returns the same VADER scores as the build."""
    examples = json.loads((SITE / "data" / "nltk_examples.json").read_text())["items"]
    page.goto(f"{site_server}/playground.html")
    expect(page.locator("#spacy-note")).to_contain_text("cannot run in the browser")
    expect(page.locator("body")).to_have_attribute("data-pyodide", "ready", timeout=180_000)
    for ex in examples[:4] + examples[-2:]:
        page.locator(f"button[data-example='{ex['id']}']").click()
        expect(page.locator("#parity")).to_be_visible(timeout=60_000)
        got = float(page.locator("#out-compound").get_attribute("data-compound"))
        assert abs(got - ex["result"]["sentiment"]["compound"]) <= 1e-4, ex["id"]
        assert float(page.locator("#parity").get_attribute("data-diff")) <= 1e-4
        expect(page.locator("#results section.panel[data-source='nltk'] .badge").first).to_have_text("NLTK")
    # free text: the box returns a score and labels it NLTK
    page.fill("#review-input", "This coffee is not good. It tastes stale and bitter.")
    page.get_by_role("button", name="Analyze").click()
    expect(page.locator("#out-label")).to_have_text("negative", timeout=60_000)
    assert not console_errors
