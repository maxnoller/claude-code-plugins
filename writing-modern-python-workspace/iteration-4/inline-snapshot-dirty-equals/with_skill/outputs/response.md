```python
import pytest
from dirty_equals import IsStr, IsNow, IsUUID
from inline_snapshot import snapshot
from pydantic import ValidationError

from your_module import User


def test_user_creation_defaults():
    user = User(name="Alice", email="alice@example.com")
    assert user.model_dump() == snapshot({
        "id": IsStr(regex=r"[0-9a-f-]{36}"),  # or IsUUID() if you prefer
        "name": "Alice",
        "email": "alice@example.com",
        "created_at": IsNow(),
    })


def test_user_ids_are_unique():
    u1 = User(name="Alice", email="a@example.com")
    u2 = User(name="Bob", email="b@example.com")
    assert u1.id != u2.id


def test_user_explicit_id():
    user = User(id="custom-id-123", name="Alice", email="alice@example.com")
    assert user.id == "custom-id-123"


def test_user_is_frozen():
    user = User(name="Alice", email="alice@example.com")
    with pytest.raises(ValidationError):
        user.name = "Bob"


def test_user_strict_mode_rejects_coercion():
    with pytest.raises(ValidationError):
        User(name=123, email="alice@example.com")  # int, not str


def test_user_missing_required_fields():
    with pytest.raises(ValidationError) as exc_info:
        User(name="Alice")  # missing email
    assert "email" in str(exc_info.value)
```

Run `pytest --inline-snapshot=fix` on first run to populate any empty `snapshot()` calls.

**Key points:**

- `IsNow()` from `dirty-equals` matches timestamps within a short window of now — no need to freeze time for this model
- `IsStr(regex=...)` validates UUID format without hardcoding the value; `IsUUID()` works too if you import it
- The frozen test uses `ValidationError` not `AttributeError` — Pydantic intercepts attribute sets and raises its own error with `frozen=True`
- The strict mode test checks that `name=123` isn't silently coerced to `"123"` — that's the main thing `strict=True` buys you

If you want to assert the `id` is a valid UUID (not just UUID-shaped string), swap to:

```python
from dirty_equals import IsUUID
"id": IsUUID(4),  # UUID version 4
```
