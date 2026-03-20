Here's the ruff setup for strict code quality enforcement.

Add to your `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["ALL"]
ignore = [
    "COM812",   # trailing comma — conflicts with formatter
    "ISC001",   # implicit string concat — conflicts with formatter
    "D",        # docstrings — enable when you're ready to enforce them
    "CPY",      # copyright headers — not needed for internal code
    "FBT",      # boolean trap — too noisy for most codebases
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "ANN", "PLR2004"]  # allow assert, skip annotations, allow magic values

[tool.ruff.format]
quote-style = "double"
docstring-code-format = true
```

Install and run:

```bash
uv add --group dev ruff
uv run ruff check .       # lint
uv run ruff check . --fix # lint + auto-fix
uv run ruff format .      # format
```

**Why `select = ["ALL"]` and then ignore?** Starting from everything and opting out is stricter than opting in — you won't silently miss new rule categories as ruff adds them. The ignores above are the ones that are genuinely noisy or conflict with the formatter, not a way to avoid fixing real issues.

**The key ignores explained:**
- `COM812` / `ISC001` — these conflict with ruff's own formatter, so they must be off
- `D` (pydocstyle) — docstring rules are all-or-nothing; enable once you commit to writing them everywhere
- `FBT` (flake8-boolean-trap) — flags `def foo(flag: bool)` as an error; too aggressive for most codebases

**For CI**, add this to your GitHub Actions workflow:

```yaml
- name: Lint
  run: uv run ruff check .
- name: Format check
  run: uv run ruff format --check .
```

Or a pre-commit hook:

```bash
uv run ruff check . && uv run ruff format --check .
```

Once your codebase is clean, you can graduate into stricter rules by removing items from `ignore` one at a time — for example, removing `"D"` to enforce docstrings on public APIs.
