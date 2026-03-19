# Package Management with uv

## Why

uv replaces the entire pip/pip-tools/poetry/pdm/virtualenv stack with a single tool written in Rust. It resolves dependencies in seconds instead of minutes, uses `pyproject.toml` as the single config file, and handles virtual environments transparently. There's no reason to use anything else in 2026.

## Project setup

```bash
uv init my-project
cd my-project
```

This creates a `pyproject.toml` and a `.python-version` file. The venv is created automatically on first `uv run`.

## Dependencies

```bash
uv add httpx pydantic sqlalchemy     # runtime dependencies
uv add --group dev pytest ruff ty    # dev dependency group
uv add --group test testcontainers   # separate test group
uv remove httpx                      # remove a dependency
uv lock                              # regenerate lockfile
uv sync                              # sync venv to lockfile
```

Dependencies live in `pyproject.toml` under `[project.dependencies]`. Dev/test dependencies go in `[dependency-groups]`:

```toml
[dependency-groups]
dev = ["ruff", "ty", "pytest"]
test = ["testcontainers", "pytest-asyncio"]
```

Control which groups are installed by default:

```toml
[tool.uv]
default-groups = ["dev", "test"]
```

## Running things

```bash
uv run pytest                  # run in managed venv
uv run python script.py        # run a script
uvx ruff check .               # run a tool without installing it
uvx ty check                   # same — ephemeral tool execution
```

`uvx` is an alias for `uv tool run`. It runs tools in temporary, isolated environments without installing them into your project.

## Tools

`uv tool` manages CLI tools installed globally — separate from project dependencies.

```bash
uv tool install ruff               # install globally, available everywhere
uv tool install ruff==0.9.0        # pin a version
uv tool install --with pytest-xdist pytest  # install with extra deps
uv tool upgrade ruff               # upgrade within version constraints
uv tool upgrade --all              # upgrade everything
uv tool list                       # see what's installed
uv tool uninstall ruff             # remove
```

Installed tools get their own isolated environments — they can't conflict with your project's dependencies. Their executables go on `PATH` so you can call them directly (`ruff check .` instead of `uv run ruff check .`).

Use `uv tool install` for tools you use across many projects (ruff, ty, pre-commit). Use `uvx` for one-off or infrequent use. Use `uv add --group dev` for tools that are part of a specific project's workflow.

## Workspaces

Workspaces organize monorepos into multiple packages with a shared lockfile. All members resolve together — one `uv.lock` for the entire workspace.

### Setup

Root `pyproject.toml`:

```toml
[project]
name = "my-workspace"
requires-python = ">=3.12"

[tool.uv]
package = false  # workspace root is not itself a package

[tool.uv.workspace]
members = ["packages/*", "apps/*"]
exclude = ["packages/experiments"]  # optional
```

Every directory matched by `members` must have its own `pyproject.toml`.

### Internal dependencies

Map workspace members as sources so they resolve locally instead of from PyPI:

```toml
[tool.uv.sources]
my-core = { workspace = true }
my-utils = { workspace = true }
```

Member dependencies on each other are editable by default. Sources defined in the workspace root apply to all members unless overridden.

### Running commands

```bash
uv run pytest                          # runs in workspace root
uv run --package my-app pytest         # runs in a specific member
uv sync                                # syncs the whole workspace
uv sync --package my-app               # syncs a specific member
```

### Workspace constraints

- All members share one `requires-python` (the intersection of all members' constraints)
- Python can't enforce dependency isolation between members — a member can import from siblings even if not declared
- If members need conflicting dependencies or different Python versions, use separate projects with path dependencies instead

### When to use workspaces

- Multiple apps sharing core packages (API + worker + CLI using shared models)
- Libraries with separate test/example packages
- Enforcing modular architecture with clear package boundaries

### When NOT to use workspaces

- Members need different Python versions
- Members have genuinely conflicting dependencies
- Simple projects with one deployable — a workspace adds structure you don't need

## Docker

uv works well in Docker. The key patterns: copy the binary from the official image, cache dependency installation separately from code changes, and compile bytecode for faster startup.

### Basic Dockerfile

```dockerfile
FROM python:3.12-slim

# copy uv binary
COPY --from=ghcr.io/astral-sh/uv:0.10 /uv /uvx /bin/

WORKDIR /app

# install dependencies first (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

# then copy source and install project
COPY . .
RUN uv sync --locked

# activate venv via PATH
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "myapp"]
```

The two-step `uv sync` is important: the first call installs dependencies only (cached as long as `pyproject.toml` and `uv.lock` don't change), the second installs your actual project code. This means code changes don't rebuild the dependency layer.

### Production optimizations

```dockerfile
# compile bytecode for faster startup
ENV UV_COMPILE_BYTECODE=1

# use copy mode instead of hardlinks (required in Docker)
ENV UV_LINK_MODE=copy

# skip dev dependencies
ENV UV_NO_DEV=1

# cache mount for faster rebuilds
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project
```

### .dockerignore

Always add `.venv` to `.dockerignore` — you don't want the host venv in the image:

```
.venv
__pycache__
.git
```

### Multi-stage builds

For minimal production images, build in one stage and copy only what's needed:

```dockerfile
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.10 /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project
COPY . .
RUN uv sync --locked

FROM python:3.12-slim
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app
CMD ["python", "-m", "myapp"]
```

## Python version

Pin in `pyproject.toml`:

```toml
[project]
requires-python = ">=3.12"
```

uv respects this and will download/manage the right Python version automatically.

## When to use

- Every Python project. There is no scenario where pip or poetry is a better choice for new projects.

## When NOT to use

- If you're contributing to an existing project that uses poetry/pdm and changing the tooling isn't your call. Match whatever the project uses.
