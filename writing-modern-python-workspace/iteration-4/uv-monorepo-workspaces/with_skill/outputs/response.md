Use **uv workspaces**. One lockfile, shared resolution, each package declares only what it needs.

## Structure

```
my-monorepo/
├── pyproject.toml          # workspace root
├── uv.lock                 # single lockfile for everything
├── packages/
│   └── shared/
│       └── pyproject.toml
├── apps/
│   ├── api/
│   │   └── pyproject.toml
│   └── cli/
│       └── pyproject.toml
```

## Root `pyproject.toml`

```toml
[tool.uv.workspace]
members = ["packages/*", "apps/*"]
```

The root has no dependencies itself — it's just the workspace definition.

## `packages/shared/pyproject.toml`

```toml
[project]
name = "shared"
version = "0.1.0"
dependencies = ["pydantic>=2.0"]
```

## `apps/api/pyproject.toml`

```toml
[project]
name = "api"
version = "0.1.0"
dependencies = [
    "fastapi>=0.100",
    "shared",           # reference by package name
]

[tool.uv.sources]
shared = { workspace = true }  # tells uv this is a local workspace member
```

## `apps/cli/pyproject.toml`

```toml
[project]
name = "cli"
version = "0.1.0"
dependencies = [
    "click>=8.0",
    "shared",
]

[tool.uv.sources]
shared = { workspace = true }
```

## Key rules

- **Each package declares only its direct dependencies.** `api` doesn't list `pydantic` just because `shared` uses it — transitive resolution handles that.
- **`uv.lock` lives at the root** and covers all members. All packages resolve together, so you'll never have version conflicts between `api` and `cli`.
- **Dev dependencies go on the package that needs them.** Put `pytest` in each app's `[dependency-groups]`, not the root.

```toml
# in apps/api/pyproject.toml
[dependency-groups]
dev = ["pytest>=8.0", "httpx>=0.27"]  # httpx for TestClient
```

## Running things

```bash
# from the root — uv resolves the right env
uv run --package api uvicorn api.main:app
uv run --package cli python -m cli

# or cd into the package
cd apps/api && uv run pytest
```

When you `uv add` a dependency, do it from inside the package directory (or pass `--package api`) so it goes into the right `pyproject.toml`, not the root.
