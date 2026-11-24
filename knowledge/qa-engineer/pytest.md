# pytest

Sources:
- https://docs.pytest.org/en/stable/getting-started.html
- https://docs.pytest.org/en/stable/how-to/fixtures.html
- https://docs.pytest.org/en/stable/how-to/parametrize.html

## Fixtures
- Declare with `@pytest.fixture`. Tests request a fixture by naming it as an argument, and fixtures can request other fixtures.
- **Scopes:** "Fixtures are created when first requested by a test, and are destroyed based on their `scope`":
  - `function`: "the default scope, the fixture is destroyed at the end of the test."
  - `class`: destroyed during teardown of the last test in the class
  - `module`, `package`, `session`: the same idea at larger levels
- Expensive fixtures go in `conftest.py` with a wider scope: "puts the fixture function into a separate `conftest.py` file so that tests from multiple test modules in the directory can access the fixture function." Use `@pytest.fixture(scope="module")` or `"session"`.
- **Teardown:** "'Yield' fixtures `yield` instead of `return`... Any teardown code for that fixture is placed *after* the `yield`." This is the recommended approach.
- `tmp_path` is a built-in fixture giving a per-test temporary directory. Use it for build-output tests.

## Parametrize
```python
@pytest.mark.parametrize("test_input,expected", [("3+5", 8), ("2+4", 6), ("6*9", 42)])
def test_eval(test_input, expected):
    assert eval(test_input) == expected
```
- It runs once per tuple, and failures show the parameter id (e.g. `test_eval[6*9-42]`). It can also decorate a class.

## Project conventions
- `@pytest.fixture(scope="session") def nlp()` loads `en_core_web_sm` once, because loading per test is slow.
- `@pytest.fixture(scope="session") def sia()` creates one VADER analyzer.
- Use golden cases via parametrize. For example, "not good" must have `compound <= -0.05`, and "The strap is flimsy" must yield `("strap", "flimsy", False)`.
