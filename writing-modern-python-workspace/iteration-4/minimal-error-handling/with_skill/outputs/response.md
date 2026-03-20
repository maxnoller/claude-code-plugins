A few things to address before writing: "error handling for every possible failure mode" is a trap — you end up with `except Exception` soup that catches things you can't meaningfully handle (like `MemoryError`). I'll handle the realistic failure modes for file I/O and JSON parsing, and use `structlog` for structured logging.

```python
import json
from pathlib import Path
from typing import Any

import structlog

log = structlog.get_logger()


def read_config(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    logger = log.bind(config_path=str(path))

    logger.debug("reading_config")

    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.error("config_not_found")
        raise
    except PermissionError:
        logger.error("config_permission_denied")
        raise
    except IsADirectoryError:
        logger.error("config_path_is_directory")
        raise
    except OSError as exc:
        logger.error("config_read_failed", error=str(exc))
        raise

    try:
        config = json.loads(text)
    except json.JSONDecodeError as exc:
        logger.error(
            "config_invalid_json",
            line=exc.lineno,
            col=exc.colno,
            detail=exc.msg,
        )
        raise

    if not isinstance(config, dict):
        msg = f"config must be a JSON object, got {type(config).__name__}"
        logger.error("config_wrong_type", got=type(config).__name__)
        raise TypeError(msg)

    logger.info("config_loaded", key_count=len(config))
    return config
```

**Key decisions:**

- **Separate read from parse** — splitting `path.read_text()` and `json.loads()` keeps I/O errors distinct from parse errors, and each gets the right context in the log.

- **Re-raise, don't swallow** — each `except` block logs and re-raises. The caller decides whether a missing config is fatal or fallback-worthy; this function shouldn't make that call.

- **`IsADirectoryError` explicitly** — it's a subclass of `OSError` but the error message is confusing without it. The three explicit cases (`FileNotFoundError`, `PermissionError`, `IsADirectoryError`) are the ones worth naming clearly.

- **Validate the shape** — `json.loads("42")` is valid JSON but breaks the `dict[str, Any]` contract. One `isinstance` check enforces it at the boundary.

- **`structlog` key=value style** — structured log events are queryable in production (Datadog, CloudWatch, etc). String interpolation in log messages is not.

- **No `except Exception`** — `OSError` covers all realistic I/O failures. Letting truly unexpected errors (e.g., `MemoryError`) propagate unmodified is correct behavior.
