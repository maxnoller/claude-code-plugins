Here's a pre-commit config using ruff (which replaces flake8, isort, black, and friends in one tool):

**`.pre-commit-config.yaml`**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff           # linter — runs ruff check --fix
        args: [--fix]
      - id: ruff-format    # formatter — runs ruff format
```

Then add ruff config to your **`pyproject.toml`**:

```toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["ALL"]
ignore = [
    "COM812",   # trailing comma — conflicts with formatter
    "ISC001",   # implicit string concat — conflicts with formatter
    "D",        # docstrings — add when you're ready to enforce them
    "CPY",      # copyright headers
    "FBT",      # boolean trap — too noisy for most codebases
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "ANN", "D", "PLR2004"]
"scripts/**" = ["INP001", "T201"]

[tool.ruff.format]
quote-style = "double"
docstring-code-format = true
```

**Install and activate:**

```bash
uv add --group dev pre-commit
uv run pre-commit install        # installs the git hook
uv run pre-commit run --all-files  # run once on existing code
```

**Why this setup:**

- `ruff-pre-commit` is the official hook — it uses a pre-built binary so it's fast (no Python environment startup per hook).
- `ruff check --fix` runs first and auto-fixes what it can; `ruff format` runs second to normalize style.
- The `select = ["ALL"]` + explicit ignores approach is better than opting in rule by rule — you get new rules automatically as ruff adds them, and you only carve out what genuinely doesn't fit.

If you also want type checking on commit, add `ty`:

```yaml
  - repo: local
    hooks:
      - id: ty
        name: ty
        entry: uvx ty check
        language: system
        types: [python]
        pass_filenames: false
```

This uses `local` + `uvx` instead of a remote repo hook because ty doesn't have an official pre-commit hook yet.
