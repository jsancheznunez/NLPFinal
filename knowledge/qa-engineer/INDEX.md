# Knowledge: qa-engineer

| File | Covers | Main sources |
|---|---|---|
| [pytest.md](pytest.md) | fixtures, scopes, `conftest.py`, yield teardown, parametrize | docs.pytest.org how-to/fixtures, how-to/parametrize, getting-started |
| [playwright.md](playwright.md) | pytest-playwright setup, CLI options, `expect` auto-retry assertions, base URL | playwright.dev/python/docs: intro, test-runners, test-assertions |
| [json-schema-validation.md](json-schema-validation.md) | Validating `site/data/*.json` with python-jsonschema | python-jsonschema.readthedocs.io validate |
| [test-plan.md](test-plan.md) | What to test for this project and where | project docs |

The cloud sandbox has Chromium and Playwright pre-installed. Don't run `playwright install` there. Run `pytest --tracing off` unless you're debugging.
