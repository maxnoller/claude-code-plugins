---
name: writing-modern-python
description: Opinionated modern Python patterns and conventions (2026). Use this skill whenever writing, reviewing, or suggesting Python code. Trigger on any Python development task — writing tests, creating models, setting up projects, choosing libraries, structuring code, configuring tooling, or making style decisions. Also trigger when the user mentions "modern python", "python best practices", "how should I write this", "python patterns", inline-snapshot, dirty-equals, pydantic, pytest, ruff, structlog, uv, ty, pyrefly, type checking, linting, or formatting. Even if the user doesn't explicitly ask for style guidance, apply these patterns when generating Python code.
---

# Writing Modern Python (2026)

Every line of code should exist for a reason. These patterns share a philosophy: choose sharp tools that do one thing well, let automation handle what humans are bad at, and never add complexity without clear intent.

When writing new Python code, apply these patterns by default. When working in an existing codebase that does things differently, match the existing style unless asked to modernize.

## Don't add without intent

This applies to everything — dependencies, abstractions, error handling, type annotations, comments. If you can't articulate why something needs to exist, it doesn't. No speculative helpers. No "just in case" wrappers. No defensive code against scenarios that can't happen. The right amount of code is the minimum that solves the actual problem.

## Package management: uv

Use `uv` for everything — installing, resolving, running, managing virtual environments. It replaces pip, pip-tools, poetry, pdm, and virtualenv. It's written in Rust, resolves in seconds, and uses `pyproject.toml` as the single source of truth. No `setup.py`, no `requirements.txt`, no `setup.cfg`.

```bash
uv init my-project              # new project with pyproject.toml
uv add httpx pydantic           # add dependencies
uv add --group dev pytest ruff  # dev dependencies in dependency groups
uv run pytest                   # run in managed venv
uv lock                         # lock dependencies
uvx ruff check .                # run a tool without installing it
```

Use `uv tool install` for CLI tools you use across projects (ruff, ty). Use `uvx` for one-off tool runs. For monorepos, use workspaces with `[tool.uv.workspace]` — all members share one lockfile and resolve together. In Docker, copy the uv binary from the official image and split `uv sync` into two steps (dependencies first, project second) for layer caching.

See `references/tooling-uv.md` for workspaces, `uv.sources` for internal packages, Docker patterns, and tool management.

## Linting and formatting: ruff

Use `ruff` for both linting and formatting — it replaces flake8, isort, black, pyflakes, and dozens of plugins. Start with all rules enabled and ignore what doesn't fit, rather than opting in rule by rule.

```toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["ALL"]
ignore = [
    "COM812",   # trailing comma — conflicts with formatter
    "ISC001",   # implicit string concat — conflicts with formatter
    "D",        # docstrings — enforce these when you're ready, not by default
    "CPY",      # copyright headers — not needed for internal code
    "FBT",      # boolean trap — too noisy for most codebases
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "ANN", "D", "PLR2004"]
"scripts/**" = ["INP001", "T201"]

[tool.ruff.format]
quote-style = "double"
docstring-code-format = true
```

Run with `ruff check .` and `ruff format .`. The formatter is a drop-in replacement for black.

See `references/tooling-ruff.md` for the full ignore rationale, per-file ignore patterns, and how to graduate into stricter rules over time.

## Type checking: ty or pyrefly

Use a Rust-based type checker — they're 10-100x faster than mypy and give better editor integration. Two good options:

**ty** (Astral, same team as ruff/uv) — strict, fast, configurable per-rule severity. Best if you're already in the Astral ecosystem.

```toml
[tool.ty.rules]
possibly-unresolved-reference = "error"
```

```bash
uvx ty check
```

**pyrefly** (Meta) — fast, aggressive type inference (infers return types and variable types automatically). Best if you want maximum inference with minimum annotations.

```toml
[tool.pyrefly]
project_includes = ["src"]
python_version = "3.12"
```

```bash
uvx pyrefly check
```

Both are young and evolving fast. Pick one per project and stay consistent. Don't run both on the same codebase.

See `references/tooling-typechecking.md` for configuration patterns, strictness levels, and per-file overrides.

## Data modeling: Pydantic

Use Pydantic when data crosses a trust boundary — API input, config files, message queues, pipeline stages. Don't use it for internal data containers where a `dataclass` or `NamedTuple` would do. The question is "does this data need validation?" not "does this data have fields?"

When you do use Pydantic, always set `ConfigDict(strict=True, frozen=True, extra="forbid")`. Strict catches silent coercion (`"123"` quietly becoming `int`), frozen prevents mutation after validation, extra rejects unknown fields. Opt out per-field, not the other way around.

```python
from pydantic import BaseModel, ConfigDict

class WebhookPayload(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    event_type: str
    timestamp: datetime
    amount: int
```

Build reusable constrained types with `Annotated` — define `PositiveInt` or `Email` once, import everywhere. Don't inline `Field(gt=0)` repeatedly.

See `references/modeling-pydantic.md` for when-to-use decision guide and the opinionated defaults.

## Testing

Let tools write your test data. Start with an empty `snapshot()`, run `pytest --inline-snapshot=fix`, and it fills in the actual output. Use `dirty-equals` matchers for values that change between runs — timestamps, IDs, UUIDs. This way tests assert on the complete shape of your data without you typing any of it by hand.

```python
from dirty_equals import IsInt, IsNow
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

Don't write per-field assertions for structured data. Don't use separate snapshot files. If the data has more than 2-3 fields, use inline snapshots.

See `references/testing-inline-snapshot.md` for the full pattern — matchers, snapshot update commands, converting complex objects to dicts.

## Profiling

Use `yappi` — it handles async and threads natively, which `cProfile` can't. Pick `cpu` clock for CPU-bound work, `wall` clock for I/O-bound or async latency.

```python
import yappi

yappi.set_clock_type("wall")
with yappi.run():
    asyncio.run(main())
yappi.get_func_stats().print_all()
```

For line-level profiling, use `py-spy` or `scalene` instead — yappi is function-level.

See `references/profiling-yappi.md` for thread-level breakdown, filtering, and exporting to callgrind/pstats.
