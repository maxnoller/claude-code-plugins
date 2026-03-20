```bash
uv init my-project
cd my-project
uv add httpx pydantic
uv add --group dev pytest ruff
```

That's it. Here's the resulting `pyproject.toml`:

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "httpx>=0.28.1",
    "pydantic>=2.10.6",
]

[dependency-groups]
dev = [
    "pytest>=8.3.5",
    "ruff>=0.9.10",
]

[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["ALL"]
ignore = [
    "COM812",
    "ISC001",
    "D",
    "CPY",
    "FBT",
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "ANN", "PLR2004"]

[tool.ruff.format]
quote-style = "double"
docstring-code-format = true
```

A few notes:

- `uv init` creates the project with a `pyproject.toml`, `.python-version`, and a basic `src/` layout
- `uv add --group dev` uses [dependency groups](https://peps.python.org/pep-0735/) (PEP 735) — the modern replacement for extras like `[dev]`. Groups are not installed by default; `uv run pytest` will include them automatically
- The ruff config starts with `select = ["ALL"]` and ignores noisy rules — this is intentionally strict. Remove rules you find too aggressive rather than opting in rule-by-rule
- Exact versions in the generated `pyproject.toml` will reflect whatever is latest when you run the commands; the ones above are illustrative

To run things:

```bash
uv run pytest          # runs tests in the managed venv
uv run ruff check .    # lint
uv run ruff format .   # format
```
