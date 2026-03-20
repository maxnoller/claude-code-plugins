For internal data that never crosses a trust boundary, use a `dataclass`:

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class UserInfo:
    user_id: int
    username: str
    roles: list[str]
    created_at: datetime
```

**Why not Pydantic here?** Pydantic is for trust boundaries — validating data from external sources (API input, config files, message queues). Since this struct is constructed internally from already-validated data, Pydantic's runtime validation is unnecessary overhead with no safety benefit.

**Why `frozen=True`?** Prevents accidental mutation as the object passes through functions. If you need to "update" it, you'd create a new instance — which is the right default for internal data carriers.

Usage:

```python
from dataclasses import replace

user = UserInfo(
    user_id=42,
    username="alice",
    roles=["admin", "editor"],
    created_at=datetime.now(tz=timezone.utc),
)

# To "modify", create a new instance
updated = replace(user, roles=[*user.roles, "viewer"])
```

If ordering or hashing matters (e.g., storing in sets/dicts), `frozen=True` also automatically makes the dataclass hashable.

The one case to reach for `NamedTuple` instead: if you need tuple unpacking or positional access. But for named field access like this, `dataclass` is cleaner.
