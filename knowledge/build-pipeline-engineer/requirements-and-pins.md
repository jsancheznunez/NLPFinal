# requirements.txt and version pins

Sources:
- https://pip.pypa.io/en/stable/reference/requirements-file-format/
- https://spacy.io/usage/models (section "Downloading and requiring package dependencies")
- PyPI JSON API (checked Nov 24 2026)
- https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide-lock.json

## pip requirements format
- "Each line of the requirements file indicates something to be installed, or arguments to pip install." Supported forms are requirement specifiers, archive URLs or paths, and `-e` paths.
- Direct references use `name @ URL`, e.g. `urllib3 @ https://github.com/.../1.26.8.zip`.
- Comments start with `#`. A trailing `\` continues the line. The default encoding is UTF-8.
- Global options on their own lines: `-c constraints.txt`, `-r other.txt`, `--only-binary`, `--require-hashes`, and others.

## spaCy model as a dependency
spaCy docs: "Because pipeline packages are valid Python packages, you can add them to your application's `requirements.txt`... pip's requirements file format supports both package names... as well as direct URLs."

## Project requirements.txt (pins and why)
```text
# Must equal the NLTK version inside Pyodide 314.0.8 (pyodide-lock.json: nltk 3.9.4)
nltk==3.9.4
# spaCy 3.8.x <-> en_core_web_sm 3.8.0 (meta: spacy_version ">=3.8.0,<3.9.0")
spacy>=3.8.0,<3.9.0
en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
pandas>=2.2,<4
jsonschema>=4.23,<5
```
- PyPI (Nov 2026): `spacy 3.8.18` (Python >=3.10,<3.16), `nltk 3.10.4` (latest, but **not** what Pyodide ships, so don't use it), `pandas 3.1.1` (Python >=3.11), `jsonschema 4.26.0`.
- After the first green build, freeze exact versions with `pip freeze` into `requirements.lock.txt` and use `-c requirements.lock.txt`, so cached and clean builds match.
- Dev-only tools (`pytest`, `pytest-playwright`) go in `requirements-dev.txt`, which Netlify doesn't install.
