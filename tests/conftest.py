"""Shared fixtures. Python tests run against the venv (requirements-dev.txt)."""
import functools
import http.server
import os
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT))

NLTK_DIR = Path(os.environ.get("NLTK_DATA_DIR", ROOT / "nltk_data")).resolve()


def pytest_configure(config):
    # Same NLTK data location the build uses; fetched once if missing (never inside analysis code).
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_analysis import ensure_nltk_data
    ensure_nltk_data(NLTK_DIR)


@pytest.fixture(scope="session")
def nlp():
    from analyzer import spacy_layer
    patterns = spacy_layer.build_patterns([
        {"store": "Olaplex", "title": "Olaplex No.3 Hair Perfector"},
        {"store": "Pure Body Naturals", "title": "Pure Body Naturals Dead Sea Salt, 5 lb"},
        {"store": "Okay", "title": "Okay Pure Naturals Shea Butter"},
    ], common_words=frozenset({"okay"}))
    return spacy_layer.load_nlp(patterns)


@pytest.fixture(scope="session")
def site_server():
    """Serve site/ like `python -m http.server -d site` on a free port.

    Set SITE_URL (e.g. https://nlpfinal-product-analyzer.netlify.app) to run the e2e tests
    against a deployed site instead. The playground test still compares with the local
    site/data/nltk_examples.json, so build locally from the same commit first.
    """
    if os.environ.get("SITE_URL"):
        yield os.environ["SITE_URL"].rstrip("/")
        return
    if not (SITE / "data" / "summary.json").exists():
        pytest.skip("site/data not built; run python scripts/build_analysis.py first")
    handler = functools.partial(QuietHandler, directory=str(SITE))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass
