# Snapshot Testing with inline-snapshot + dirty-equals

## Why

Traditional per-field assertions are tedious and incomplete — you only test the fields you remembered to assert on. Separate snapshot files (syrupy) force context-switching between files. Inline snapshots keep everything visible in the test file and auto-update when data structures change.

## The pattern

Start with an empty `snapshot()`, then run `pytest --inline-snapshot=fix` to auto-populate:

```python
from inline_snapshot import snapshot

def test_user_creation():
    user = create_user(id=123, name="test_user")
    assert user.model_dump() == snapshot()
```

After running the fix command, this becomes:

```python
def test_user_creation():
    user = create_user(id=123, name="test_user")
    assert user.model_dump() == snapshot({
        "id": 123,
        "name": "test_user",
        "status": "active",
        "created_at": "2026-03-19T12:00:00Z",
    })
```

## Dynamic values with dirty-equals

Values like timestamps, auto-generated IDs, and UUIDs change between runs. Use `dirty-equals` matchers for these instead of ignoring them:

```python
from dirty_equals import IsInt, IsNow, IsUUID
from inline_snapshot import snapshot

def test_user_creation():
    user = create_user(name="test_user")
    assert user.model_dump() == snapshot({
        "id": IsInt(),
        "name": "test_user",
        "status": "active",
        "created_at": IsNow(iso_string=True),
    })
```

### Common matchers

- `IsInt()`, `IsPositiveInt()`, `IsFloat()` — numeric types
- `IsStr()`, `IsStr(regex=r"^usr_")` — strings, optionally with pattern
- `IsUUID()` — any UUID
- `IsNow()`, `IsNow(iso_string=True)` — datetime close to now
- `IsUrl()` — any valid URL

## Converting complex objects to dicts

Convert Pydantic models or dataclasses to plain dicts so snapshots stay resilient to signature changes:

```python
from pydantic import TypeAdapter

_adapter = TypeAdapter(object)

def as_dicts(value: object):
    return _adapter.dump_python(value)

def test_complex_response():
    response = get_response()
    assert as_dicts(response) == snapshot()
```

## Updating snapshots

```bash
pytest --inline-snapshot=fix      # auto-fill empty snapshots
pytest --inline-snapshot=update   # update all snapshots to match current output
pytest --inline-snapshot=review   # review changes before applying
```

## When to use

- Testing API responses, Pydantic models, dataclass outputs
- Any test where the expected data has more than 2-3 fields
- When data structures are still evolving

## When NOT to use

- Simple boolean or single-value assertions (`assert is_valid is True`)
- Tests where the exact assertion logic is the point (boundary conditions, edge cases)
