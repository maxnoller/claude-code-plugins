```python
from typing import Protocol, Self, runtime_checkable


@runtime_checkable
class JsonSerializable(Protocol):
    def to_json(self) -> str: ...

    @classmethod
    def from_json(cls, data: str) -> Self: ...
```

`Self` (from `typing`, available since 3.11 — use `typing_extensions` for 3.10) ensures `from_json` returns the concrete subclass, not the base type.

`@runtime_checkable` lets you use `isinstance(obj, JsonSerializable)` at runtime — without it, Protocol checks are type-checker-only.

**Usage with a Pydantic model** (the common case at a trust boundary):

```python
import json
from pydantic import BaseModel, ConfigDict


class WebhookPayload(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    event_type: str
    amount: int

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, data: str) -> "WebhookPayload":
        return cls.model_validate_json(data)


# Satisfies the protocol structurally — no explicit inheritance needed
payload: JsonSerializable = WebhookPayload(event_type="purchase", amount=100)
assert isinstance(payload, JsonSerializable)  # works at runtime
```

**Usage with a plain dataclass** (for internal data that doesn't need Pydantic):

```python
import json
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, data: str) -> "Point":
        return cls(**json.loads(data))
```

Key design notes:
- Protocol uses **structural subtyping** — any class with matching `to_json`/`from_json` signatures satisfies it without explicit inheritance.
- `Self` is critical for `from_json`: without it, the type checker thinks every `from_json` returns a `JsonSerializable`, losing the concrete type downstream.
- If you're on Python 3.10, swap `Self` for `typing_extensions.Self` and add `typing-extensions` as a dependency via `uv add typing-extensions`.
