# Type Checking with ty or pyrefly

## Why not mypy

mypy is slow, its configuration is complex, and its error messages are often unhelpful. Rust-based type checkers are 10-100x faster, give better diagnostics, and integrate more smoothly with editors. In 2026, there's no reason to start a new project with mypy.

## Choosing between ty and pyrefly

Both are fast, Rust-based, and actively developed. They have different philosophies:

**ty** (Astral — same team as ruff and uv)
- Configurable per-rule severity levels
- Per-file overrides
- Suppression comments
- First-class intersection types
- Fits naturally if you're already using ruff + uv

**pyrefly** (Meta)
- Aggressive type inference — infers return types and variable types automatically
- Flow-sensitive types (knows `x` is `Literal[4]` right after `x: int = 4`)
- Module-level incrementality with parallelism
- Originated from Meta's Pyre ecosystem

Pick one per project and stay consistent. Don't run both — they'll disagree on edge cases and create noise.

## ty configuration

### Minimal setup

```toml
[tool.ty]
python-version = "3.12"
```

```bash
uvx ty check
```

### Strict setup

Promote specific rules to errors:

```toml
[tool.ty.rules]
possibly-unresolved-reference = "error"
possibly-missing-module-member = "error"
possibly-missing-attribute = "error"
```

### Per-file overrides

Relax rules for tests or specific directories:

```toml
[[tool.ty.overrides]]
path = "tests/**"
[tool.ty.overrides.rules]
possibly-unresolved-reference = "warn"

[[tool.ty.overrides]]
path = "scripts/**"
[tool.ty.overrides.rules]
unresolved-import = "warn"
```

### Environment configuration

```toml
[tool.ty.environment]
python-version = "3.12"
```

## pyrefly configuration

### Minimal setup

```toml
[tool.pyrefly]
project_includes = ["src"]
python_version = "3.12"
```

```bash
uvx pyrefly check
```

### Type inference behavior

pyrefly infers more aggressively than ty:

```python
# pyrefly infers return type as bool — no annotation needed
def is_valid(x):
    return x > 0

# pyrefly infers list type from usage
xs = []
xs.append(1)      # xs is List[int]
xs.append("")     # error: str is not int
```

This means you write fewer annotations, but you may get surprising errors when pyrefly's inference disagrees with your intent. Add explicit annotations when the inferred type isn't what you want.

## General type checking patterns

Regardless of which checker you use:

### Modern syntax only

```python
# yes
def greet(name: str | None) -> str: ...
items: list[str] = []
mapping: dict[str, int] = {}

# no — never use these
from typing import Optional, List, Dict
from __future__ import annotations  # not needed on 3.12+
```

### NewType for domain IDs

Prevent mixing incompatible identifiers:

```python
from typing import NewType

UserId = NewType("UserId", str)
OrderId = NewType("OrderId", str)

def get_order(order_id: OrderId) -> Order: ...

# type error: UserId is not OrderId
get_order(UserId("usr_123"))
```

### Protocols for structural typing

When you need an interface without inheritance:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Sendable(Protocol):
    def send(self, message: str) -> None: ...
```

## When to use

- Every Python project should have a type checker. Pick ty or pyrefly based on which ecosystem you prefer.

## When NOT to use

- Quick scripts or notebooks where you won't benefit from type safety. But if it's going into production, type check it.
