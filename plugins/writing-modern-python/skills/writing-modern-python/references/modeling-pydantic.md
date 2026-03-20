# Data Modeling with Pydantic v2

## Why

Pydantic is the data validation layer for modern Python — FastAPI, LangChain, and most serious frameworks build on it. v2 rewrote the core in Rust, making it 5-50x faster than v1. More importantly, v2's `Annotated` pattern lets you build reusable constrained types that compose cleanly — define `PositiveInt` or `Email` once, use them everywhere.

## Models

Use `BaseModel` for structured data with validation. Default to strict and frozen for API models — catch type bugs at the boundary, not deep in your business logic.

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    id: int
    name: str
    email: str
```

### Key methods

| Method | Use |
|---|---|
| `Model(field=val)` | Validate via constructor |
| `Model.model_validate(data)` | Validate a dict |
| `Model.model_validate_json(raw)` | Parse + validate JSON (fastest path — skip `json.loads()`) |
| `m.model_dump()` | To dict |
| `m.model_dump_json()` | To JSON bytes |
| `m.model_copy(update={...})` | Clone with changes |
| `m.model_fields_set` | Which fields the caller actually provided |

`model_validate_json()` is faster than `json.loads()` + `model_validate()` — it parses and validates in one Rust pass. Always prefer it when you have raw JSON.

### Immutability

`ConfigDict(frozen=True)` makes instances immutable. Use `model_copy(update={...})` to create modified copies. Note: only shallow — nested mutables are still mutable.

### Extra fields

```python
model_config = ConfigDict(extra="forbid")  # Reject unknown fields — use for API input
```

### RootModel for wrapper types

```python
from pydantic import RootModel

UserIds = RootModel[list[int]]
ids = UserIds.model_validate_json(b"[1, 2, 3]")
ids.root  # [1, 2, 3]
```

### Generic models

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    data: T
    error: str | None = None

Response[int](data=42)
```

Python 3.12+: `class Response[T](BaseModel): ...`

## Fields

Use `Field()` for constraints, aliases, and behavior. Use `Annotated` for reusable constrained types.

```python
from typing import Annotated
from pydantic import Field

# Reusable constrained types — the v2 superpower
PositiveInt = Annotated[int, Field(gt=0)]
NonEmptyStr = Annotated[str, Field(min_length=1)]
Email = Annotated[str, Field(pattern=r"^[\w.-]+@[\w.-]+\.\w+$")]

class Product(BaseModel):
    price: PositiveInt
    name: NonEmptyStr
    sku: str = Field(pattern=r"^[A-Z]{3}-\d{4}$")
```

### Aliases for API boundaries

```python
class Event(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    created_at: datetime = Field(alias="createdAt")           # Both directions
    updated_at: datetime = Field(validation_alias="updatedAt")  # Input only
    user_name: str = Field(serialization_alias="userName")      # Output only
```

Use `alias` when input and output use the same name (e.g., camelCase API). Use `validation_alias` / `serialization_alias` when they differ.

### Other useful Field parameters

- `exclude=True` — never serialized (passwords, internal IDs)
- `repr=False` — hidden from `repr()` too
- `frozen=True` — immutable per-field
- `default_factory=list` — mutable defaults done right
- `deprecated="Use X instead"` — soft deprecation warnings
- `strict=True` — no coercion for this field (even if model is lax)

### v2 breaking change

`Optional[X]` no longer auto-defaults to `None`. Write `field: str | None = None` explicitly.

## Validators

Two patterns: `Annotated` validators for reusable single-field logic, decorator validators for model-specific or cross-field logic.

### Annotated validators (reusable)

```python
from typing import Annotated
from pydantic import AfterValidator

NonEmptyStr = Annotated[str, AfterValidator(lambda v: v if v.strip() else (_ for _ in ()).throw(ValueError("empty")))]
Trimmed = Annotated[str, AfterValidator(str.strip)]
```

### field_validator (model-specific)

```python
from pydantic import field_validator

class User(BaseModel):
    name: str

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v
```

Modes: `before` (raw input, use for coercion), `after` (parsed type, use for validation), `wrap` (around parsing, use for error recovery), `plain` (replaces parsing entirely).

### model_validator (cross-field)

```python
from typing_extensions import Self

class DateRange(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def check_range(self) -> Self:
        if self.start >= self.end:
            raise ValueError("start must be before end")
        return self
```

Use `mode="after"` for cross-field validation (self is fully constructed). Use `mode="before"` to reject or transform raw input before any field parsing.

## Computed fields

```python
from pydantic import computed_field

class Circle(BaseModel):
    radius: float

    @computed_field
    @property
    def area(self) -> float:
        return 3.14159 * self.radius ** 2
```

Appears in `model_dump()` and JSON Schema automatically. Use `@cached_property` (requires `frozen=True`) for expensive computations.

## Serialization

### model_dump() parameters that matter

```python
m.model_dump(
    mode="json",            # JSON-safe types (datetime -> str, etc.)
    by_alias=True,          # Use alias names
    exclude_unset=True,     # Only fields the caller provided — the PATCH pattern
    exclude_none=True,      # Omit None values
    include={"id", "name"}, # Whitelist
    exclude={"password"},   # Blacklist
)
```

**The PATCH pattern**: `exclude_unset=True` gives you only the fields the client actually sent — perfect for partial updates. Not the same as `exclude_none` (a field explicitly set to `None` is different from a field not sent at all).

### Custom serializers

```python
from pydantic import field_serializer, PlainSerializer

# Decorator (model-specific)
class Event(BaseModel):
    when: datetime

    @field_serializer("when")
    def serialize_when(self, v: datetime, _info) -> str:
        return v.strftime("%Y-%m-%d")

# Annotated (reusable)
ISODatetime = Annotated[datetime, PlainSerializer(lambda v: v.isoformat(), return_type=str)]
```

### Subclass serialization

v2 strips subclass-only fields by default. Use `SerializeAsAny` when you need them:

```python
from pydantic import SerializeAsAny

class Container(BaseModel):
    user: SerializeAsAny[User]  # Subclass fields included in output
```

## Discriminated unions

Always use discriminated unions for polymorphic model types. They're O(1) lookup vs O(n) trial-and-error, and produce clear error messages.

```python
from typing import Literal, Union
from pydantic import BaseModel, Field

class Cat(BaseModel):
    pet_type: Literal["cat"]
    meows: int

class Dog(BaseModel):
    pet_type: Literal["dog"]
    barks: float

class Owner(BaseModel):
    pet: Union[Cat, Dog] = Field(discriminator="pet_type")
```

For types without a shared field name, use `Discriminator` with a callable:

```python
from pydantic import Discriminator, Tag

def get_type(v: Any) -> str:
    if isinstance(v, dict):
        return v.get("type")
    return getattr(v, "type", None)

Item = Annotated[
    Annotated[Foo, Tag("foo")] | Annotated[Bar, Tag("bar")],
    Discriminator(get_type),
]
```

## TypeAdapter

Validate anything without BaseModel. Create once at module level — schema building is expensive.

```python
from pydantic import TypeAdapter

# Module level
_ids_adapter = TypeAdapter(list[int])

# In function
def parse_ids(raw: bytes) -> list[int]:
    return _ids_adapter.validate_json(raw)

# JSON Schema generation
schema = _ids_adapter.json_schema()
```

Never construct a TypeAdapter inside a hot loop.

## Strict mode

Three levels: per-call, per-field, per-model.

```python
# Per-model with per-field opt-out
class ApiRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    count: int                          # strict — "123" rejected
    score: float = Field(strict=False)  # opted out — "3.14" coerced
```

Strict mode blocks: `"123"` -> `int`, `1` -> `float`, `"true"` -> `bool`. Exception: JSON input still allows strings for dates/datetimes since JSON has no native date type.

Default to `ConfigDict(strict=True)` for API request models. Coercion bugs are silent and dangerous.

## When to use

- API request/response models (FastAPI, Django Ninja)
- Configuration parsing and validation
- Data pipeline stage boundaries
- Domain objects with invariants (cross-field validation)
- Anywhere you'd reach for a dataclass but need validation

## When NOT to use

- Pure data containers with no validation needs — use `dataclasses` or `NamedTuple`
- Hot inner loops where nanoseconds matter — Pydantic is fast but not free
- Simple key-value config — `os.environ` or a plain dict may be enough
