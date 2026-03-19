# Linting and Formatting with ruff

## Why

ruff replaces flake8, isort, black, pyflakes, pycodestyle, pydocstyle, and their plugins — all in one tool written in Rust. It runs in milliseconds, uses `pyproject.toml`, and handles both linting and formatting. There's no reason to run multiple tools anymore.

## Philosophy: start strict, ignore deliberately

Enable all rules with `select = ["ALL"]`, then ignore specific rules with documented reasons. This is the opposite of most setups (opt-in rule by rule), and it's better because:

- New rules are automatically active — you benefit from improvements without config changes
- Every ignore is a deliberate decision, not an oversight
- The ignore list documents exactly where you've chosen to be lenient

## Base configuration

```toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["ALL"]
ignore = [
    # Formatter conflicts — these rules fight with ruff format
    "COM812",   # missing trailing comma
    "ISC001",   # implicit string concatenation

    # Docstrings — opt in when ready, don't force from day one
    "D",        # all pydocstyle rules

    # Noise — these fire too often without adding value
    "CPY",      # copyright headers (internal code doesn't need them)
    "FBT",      # boolean trap (flags as args are fine in most cases)
]

[tool.ruff.format]
quote-style = "double"
docstring-code-format = true
```

## Per-file ignores

Different files have different rules. Tests shouldn't need type annotations. Scripts can use `print()`. Migrations are generated code.

```toml
[tool.ruff.lint.per-file-ignores]
# Tests: assert is fine, annotations not required, magic numbers ok
"tests/**" = ["S101", "ANN", "D", "PLR2004"]

# Scripts: print() is expected, doesn't need to be a package
"scripts/**" = ["INP001", "T201"]

# Alembic migrations: generated code, don't lint heavily
"**/migrations/**" = ["E501", "ANN"]

# CLI entry points: typer uses mutable defaults, complexity is expected
"**/cli/**" = ["B008", "C901", "PLR0915"]
```

## Graduating into stricter rules

Start lenient, tighten over time:

1. **Day one**: ignore `D` (docstrings), `ANN` (annotations), `PLR2004` (magic numbers)
2. **When stabilizing**: remove `D` from ignores, add `[tool.ruff.lint.pydocstyle]` with `convention = "google"`
3. **For libraries**: remove `ANN` from ignores to enforce full type annotations
4. **For strict codebases**: remove `PLR2004` and replace magic numbers with named constants

## Ignore rationale reference

Common ignores and why:

| Rule | What it catches | Why you might ignore it |
|------|----------------|------------------------|
| `COM812` | Missing trailing comma | Conflicts with ruff formatter |
| `ISC001` | Implicit string concat | Conflicts with ruff formatter |
| `D` | Missing docstrings | Too noisy early on — add when codebase stabilizes |
| `CPY` | Missing copyright | Not needed for internal/private code |
| `FBT` | Boolean args | Flags are fine; over-zealous |
| `E501` | Line too long | Formatter handles line length — let it |
| `PLR2004` | Magic numbers | Sometimes `if retries > 3` is clearer than a constant |
| `DOC` | Docstring content issues | Overlaps with `D`, pick one |
| `S101` | Use of `assert` | Required in tests |
| `ANN` | Missing annotations | Not always needed in tests/scripts |
| `INP001` | Missing `__init__.py` | Scripts aren't packages |
| `T201` | `print()` found | Expected in scripts and CLIs |

## Running

```bash
ruff check .              # lint
ruff check . --fix        # lint and auto-fix
ruff format .             # format (replaces black)
ruff format . --check     # check formatting without changing files
```

## When to use

- Every Python project. ruff is the linter and formatter.

## When NOT to use

- If the project already uses black + flake8 and switching isn't your call. But if you're setting up a new project or have the authority to modernize, switch.
