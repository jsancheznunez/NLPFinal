# Playwright (Python, pytest plugin)

Sources:
- https://playwright.dev/python/docs/intro
- https://playwright.dev/python/docs/test-runners
- https://playwright.dev/python/docs/test-assertions

## Setup
- "Playwright recommends using the official Playwright Pytest plugin to write end-to-end tests. It provides context isolation, running it on multiple browser configurations out of the box."
- `pip install pytest-playwright`, then `playwright install` (**skip it in the cloud sandbox**, where the browsers are pre-installed). Run with `pytest`.
- "By default tests will be run on chromium... Tests are run in headless mode."

## CLI options (test-runners)
- `--browser webkit|firefox|chromium`, `--headed`
- `--tracing on|off|retain-on-failure` (default `off`)
- **`--base-url http://localhost:8080`** (from the `pytest-base-url` plugin). Point it at a local static server or a Netlify **Deploy Preview URL**.
- Defaults can go in `pytest.ini`/`pyproject` `addopts`.

## Example (docs)
```python
import re
from playwright.sync_api import Page, expect

def test_has_title(page: Page):
    page.goto("https://playwright.dev/")
    expect(page).to_have_title(re.compile("Playwright"))
```

## Assertions
- `expect(locator).to_have_text(...)`: "Playwright will re-test the element... until it has the "Submitted" text... until the condition is met or the timeout is reached."
- "By default, the timeout for assertions is 5 seconds." The Pyodide playground needs a longer timeout on first load: `expect(loc).to_have_text(..., timeout=60_000)`.
- Other assertions: `to_be_visible()`, `to_contain_text()`. `expect.soft(...)` keeps the test running after a failure.
- Prefer role-based locators: `page.get_by_role("button", name="Analyze")`.

## Console errors
Collect them with `page.on("console", lambda m: errors.append(m) if m.type == "error" else None)` and assert the list is empty at the end of each test.
