"""scripts/build_analysis.py on tests/fixtures: expected files, schema-valid, deterministic, browser copies."""
import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_analysis  # noqa: E402

from analyzer import nltk_layer  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"


def digest(site: Path) -> dict:
    return {p.relative_to(site).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(site.rglob("*")) if p.is_file() and p.name != "build_info.json"}


@pytest.fixture(scope="module")
def two_builds(tmp_path_factory):
    nltk_dir = Path(build_analysis.ROOT / "nltk_data")
    a, b = tmp_path_factory.mktemp("site_a"), tmp_path_factory.mktemp("site_b")
    info = build_analysis.build(FIXTURES, a, nltk_dir, budget=300)
    build_analysis.build(FIXTURES, b, nltk_dir, budget=300)
    return a, b, info


def test_expected_outputs(two_builds):
    site, _, info = two_builds
    for rel in ["summary.json", "products.json", "aspects.json", "trends.json", "nltk_examples.json", "build_info.json"]:
        assert (site / "data" / rel).exists(), rel
    assert len(list((site / "data" / "product").glob("*.json"))) == info["sample"]["n_products"] == 5
    assert (site / "py" / "nltk_layer.py").read_bytes() == (ROOT / "analyzer" / "nltk_layer.py").read_bytes()
    for z in ["sentiment/vader_lexicon.zip", "corpora/stopwords.zip", "tokenizers/punkt_tab.zip"]:
        assert (site / "nltk_data" / z).stat().st_size > 1000, z
    assert (site / "displacy" / "entities.html").exists()


def test_deterministic(two_builds):
    a, b, _ = two_builds
    da, db = digest(a), digest(b)
    assert da == db


def test_browser_punkt_zip_is_english_only(two_builds):
    import zipfile
    site = two_builds[0]
    names = zipfile.ZipFile(site / "nltk_data" / "tokenizers" / "punkt_tab.zip").namelist()
    assert any(n.startswith("punkt_tab/english/") for n in names)
    assert not any(n.startswith("punkt_tab/german/") for n in names)


def test_nltk_examples_reproduce_in_cpython(two_builds):
    import json
    doc = json.loads((two_builds[0] / "data" / "nltk_examples.json").read_text())
    for item in doc["items"]:
        assert nltk_layer.analyze(item["text"]) == item["result"]


def test_build_fails_on_budget(tmp_path):
    with pytest.raises(SystemExit):
        build_analysis.build(FIXTURES, tmp_path, ROOT / "nltk_data", budget=0.0)
