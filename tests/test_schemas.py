"""schemas/*.schema.json are valid, and every built site/data file validates (allow_nan=False)."""
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from analyzer import contract

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "site" / "data"
SCHEMAS = sorted((ROOT / "schemas").glob("*.schema.json"))


@pytest.mark.parametrize("path", SCHEMAS, ids=lambda p: p.name)
def test_check_schema(path):
    Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


def built_files():
    return sorted(DATA.rglob("*.json")) if DATA.exists() else []


@pytest.mark.skipif(not built_files(), reason="site/data not built")
def test_every_built_file_validates():
    files = built_files()
    assert len(files) > 6
    bad = {}
    for f in files:
        rel = f.relative_to(DATA).as_posix()
        obj = json.loads(f.read_text(encoding="utf-8"), parse_constant=_reject_nan)
        errs = contract.errors(contract.schema_for(rel), obj)
        if errs:
            bad[rel] = errs[:3]
    assert not bad, bad


@pytest.mark.skipif(not built_files(), reason="site/data not built")
def test_every_section_is_labelled_by_library():
    s = json.loads((DATA / "summary.json").read_text())
    assert {s[k]["source"] for k in ("nltk", "spacy", "aspects", "metrics")} == {"nltk", "spacy", "spacy+nltk", "metrics"}
    p = json.loads((DATA / "products.json").read_text())["products"][0]
    assert [p[k]["source"] for k in ("metrics", "nltk", "spacy", "aspects")] == ["metrics", "nltk", "spacy", "spacy+nltk"]
    assert p["metrics"]["metric_kind"] == "proxy"


def _reject_nan(token):
    raise ValueError(f"non-JSON constant {token}")
