"""JSON contract helpers: load schemas/*.schema.json and validate outputs.

Schemas reference each other by relative $ref (e.g. "nltk_analysis.schema.json#/$defs/term"),
resolved against their $id through a `referencing` registry.
Source: https://python-jsonschema.readthedocs.io/en/stable/validate/ and
https://python-jsonschema.readthedocs.io/en/stable/referencing/
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"


@lru_cache(maxsize=1)
def registry() -> Registry:
    resources = []
    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        resources.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(resources)


@lru_cache(maxsize=None)
def validator(name: str) -> Draft202012Validator:
    """name: 'summary', 'products', 'product', 'aspects', 'trends', 'build_info', 'nltk_examples', 'nltk_analysis'."""
    schema = json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, registry=registry())


def errors(name: str, obj) -> list:
    return [f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
            for e in sorted(validator(name).iter_errors(obj), key=lambda e: list(map(str, e.path)))]


def validate(name: str, obj) -> None:
    errs = errors(name, obj)
    if errs:
        raise ValueError(f"{name}.schema.json: {len(errs)} error(s):\n  " + "\n  ".join(errs[:20]))


def schema_for(rel_path: str) -> str:
    """Map a site/data relative path to its schema name."""
    rel = rel_path.replace("\\", "/")
    if rel.startswith("product/"):
        return "product"
    return rel.rsplit("/", 1)[-1].removesuffix(".json")
