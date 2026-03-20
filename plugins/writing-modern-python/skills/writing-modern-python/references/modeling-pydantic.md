# Data Modeling with Pydantic v2

## Why

Pydantic is for data that crosses a trust boundary — where the shape and types aren't guaranteed by your own code. The validation overhead is worth it at those seams. It's not worth it for internal data containers where a `dataclass` is simpler and faster.

## When to use Pydantic

- **API input/output** — request bodies, response models, webhook payloads
- **Config files** — YAML/JSON/TOML parsed into structured objects
- **Message queues** — JSON bytes from Kafka, RabbitMQ, SQS
- **Pipeline boundaries** — data entering or leaving a processing stage
- **Domain objects with cross-field invariants** — date ranges, monetary amounts with currency

## When NOT to use Pydantic

- **Internal data containers** — use `dataclass` or `NamedTuple`. No validation needed when your own code is the producer.
- **Hot inner loops** — Pydantic is fast but not free. Validate once at the boundary, then pass plain objects through the pipeline.
- **Simple key-value config** — `os.environ` or a dict is fine for a few env vars.
- **Replacing all classes** — not everything needs to be a model. A plain class with `__init__` is fine for behavior-heavy objects.

## The opinionated defaults

Every boundary model gets this. No exceptions, then opt out per-field where needed:

```python
model_config = ConfigDict(strict=True, frozen=True, extra="forbid")
```

**Why strict**: Without it, `"123"` silently becomes `int(123)`. That's a bug hiding in production. Strict mode makes type mismatches loud. Opt out per-field with `Field(strict=False)` when coercion is intentional (e.g., accepting string dates).

**Why frozen**: Validated data shouldn't change. Use `model_copy(update={...})` for modified copies. Also enables `@cached_property` on computed fields.

**Why extra="forbid"**: Rejects unknown fields. Catches typos in config, version mismatches in APIs, and stale fields in serialized data.

## The `Annotated` pattern

Define constrained types once, import everywhere. This is the v2 pattern worth internalizing:

```python
from typing import Annotated
from pydantic import Field

PositiveInt = Annotated[int, Field(gt=0)]
NonEmptyStr = Annotated[str, Field(min_length=1)]
```

Don't inline `Field(gt=0)` on every model field. Don't create custom validator classes for simple constraints.

## The PATCH pattern

`model_dump(exclude_unset=True)` — not `exclude_none`, not manual `model_fields_set` iteration. A field explicitly set to `None` (intentional clear) is different from a field not sent (leave unchanged).

## v2 gotcha

`Optional[X]` no longer auto-defaults to `None`. Write `field: str | None = None` explicitly.
