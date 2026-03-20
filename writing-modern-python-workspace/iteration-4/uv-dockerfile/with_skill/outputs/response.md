```dockerfile
FROM python:3.12-slim AS base

# Copy uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (separate layer for caching)
FROM base AS deps
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Install the project itself
COPY . .
RUN uv sync --frozen --no-dev

FROM base AS runtime
COPY --from=deps /app /app

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]
```

**Key decisions:**

- **Two-stage `uv sync`** — dependencies install before copying your source code, so Docker reuses the cached layer on every code-only change. Only a `pyproject.toml`/`uv.lock` change invalidates it.
- **`--frozen`** — enforces the lockfile exactly, no resolution at build time.
- **`--no-dev`** — excludes dev dependencies from the production image.
- **`UV_LINK_MODE=copy`** — required in Docker since hardlinks don't work across layers.
- **`UV_COMPILE_BYTECODE=1`** — compiles `.pyc` files at build time so startup is faster at runtime.

**Adjust the CMD** based on how you run FastAPI:

```dockerfile
# If using uvicorn directly:
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# If using gunicorn for production:
CMD ["gunicorn", "src.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

Also add a `.dockerignore` to keep the image lean:

```
.venv/
.git/
__pycache__/
*.pyc
tests/
.env*
```
