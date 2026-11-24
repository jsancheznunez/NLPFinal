# Validating JSON output

Sources:
- https://python-jsonschema.readthedocs.io/en/stable/validate/
- https://json-schema.org/learn/getting-started-step-by-step

- `jsonschema.validate(instance, schema, cls=None, ...)`: "Validate an instance under the given schema." It "will first verify that the provided schema is itself valid".
- When validating many files against the same schema, build a validator once: `Draft202012Validator(schema)`. Use `Draft202012Validator.check_schema(schema)` to check the schema itself, and `validator.iter_errors(instance)` to collect **all** errors instead of stopping at the first.
- "If [format_checker is] unprovided, *no* format validation is done." Pass `format_checker=Draft202012Validator.FORMAT_CHECKER` if schemas use `"format": "date-time"`.

```python
import json, pathlib
from jsonschema import Draft202012Validator
for schema_path in pathlib.Path("schemas").glob("*.schema.json"):
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    v = Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
    data = json.loads((pathlib.Path("site/data") / schema_path.name.replace(".schema", "")).read_text())
    errors = sorted(v.iter_errors(data), key=lambda e: e.path)
    assert not errors, "\n".join(f"{list(e.path)}: {e.message}" for e in errors)
```
