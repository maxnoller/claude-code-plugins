```python
from collections.abc import Sequence
from typing import Any


def get_user(user_id: int, include_deleted: bool = False) -> User | None:
    ...


def merge_configs(*configs: dict[str, Any]) -> dict[str, Any]:
    ...


def find_items(
    names: Sequence[str],
    scores: Sequence[float],
    threshold: float | None = None,
) -> list[str]:
    ...
```

A few notes:

- `User | None` — use `X | None` (Python 3.10+) instead of `Optional[X]`.
- `Sequence[str]` over `list[str]` for inputs — accepts lists, tuples, or anything iterable with length. Use `list` for outputs since you control what you return.
- `dict[str, Any]` for `*configs` annotates the type of each individual config argument, not the tuple.
- No Pydantic here — these are internal functions with trusted data, so plain type hints are the right tool.

Adjust `User | None` to whatever your actual return type is. If `get_user` never returns `None`, drop the `| None`.
