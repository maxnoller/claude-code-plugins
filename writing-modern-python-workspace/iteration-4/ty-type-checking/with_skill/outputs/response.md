Since you're in the Astral ecosystem (uv + ruff), **ty** is the natural fit — same team, same philosophy.

## Install ty

```bash
uv add --group dev ty
```

Or for cross-project use:
```bash
uv tool install ty
```

## Configure in pyproject.toml

```toml
[tool.ty]
python-version = "3.12"  # match your target

[tool.ty.rules]
possibly-unresolved-reference = "error"
```

## Run it

```bash
uv run ty check
# or if installed as a tool:
uvx ty check
```

## Add to CI / pre-commit

If you have a `Makefile`:
```makefile
check:
    ruff check .
    ruff format --check .
    ty check
```

Or as a pre-commit hook in `.pre-commit-config.yaml`:
```yaml
- repo: local
  hooks:
    - id: ty
      name: ty
      entry: uv run ty check
      language: system
      types: [python]
      pass_filenames: false
```

## Alternative: pyrefly

If you want aggressive **type inference** (infers return types without annotations), use pyrefly instead:

```bash
uv add --group dev pyrefly
```

```toml
[tool.pyrefly]
project_includes = ["src"]
python_version = "3.12"
```

```bash
uv run pyrefly check
```

**Pick one** — don't run both on the same codebase.

---

**My recommendation**: start with `ty`. It's strict but configurable per-rule, integrates well with the Astral toolchain, and is actively developed. If ty flags too many errors at once in an existing codebase, you can silence specific rules while you work through the backlog:

```toml
[tool.ty.rules]
possibly-unresolved-reference = "warn"  # warn first, upgrade to "error" later
```
