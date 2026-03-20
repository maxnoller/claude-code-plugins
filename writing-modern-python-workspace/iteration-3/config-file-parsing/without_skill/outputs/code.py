"""Config file parsing for a CLI database sync tool.

Expects a YAML config file with the following structure:

    database:
      host: localhost
      port: 5432
      dbname: mydb
      username: user
      password: secret

    tables:
      - users
      - orders
      - products

    retry:                  # optional
      max_retries: 3
      backoff_factor: 0.5
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class DatabaseConfig:
    host: str
    port: int
    dbname: str
    username: str
    password: str


@dataclass
class RetryConfig:
    max_retries: int = 3
    backoff_factor: float = 0.5


@dataclass
class AppConfig:
    database: DatabaseConfig
    tables: list[str]
    retry: RetryConfig = field(default_factory=RetryConfig)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


class ConfigError(ValueError):
    """Raised when the config file is missing required fields or has bad values."""


def _parse_database(raw: Any) -> DatabaseConfig:
    if not isinstance(raw, dict):
        raise ConfigError("'database' must be a mapping.")

    required = ("host", "port", "dbname", "username", "password")
    missing = [k for k in required if k not in raw]
    if missing:
        raise ConfigError(f"'database' is missing required keys: {missing}")

    host = raw["host"]
    if not isinstance(host, str) or not host.strip():
        raise ConfigError("'database.host' must be a non-empty string.")

    port = raw["port"]
    if not isinstance(port, int) or isinstance(port, bool):
        raise ConfigError("'database.port' must be an integer.")
    if not (1 <= port <= 65535):
        raise ConfigError(f"'database.port' must be between 1 and 65535, got {port}.")

    dbname = raw["dbname"]
    if not isinstance(dbname, str) or not dbname.strip():
        raise ConfigError("'database.dbname' must be a non-empty string.")

    username = raw["username"]
    if not isinstance(username, str) or not username.strip():
        raise ConfigError("'database.username' must be a non-empty string.")

    password = raw["password"]
    # Password may be an integer/float in YAML if user forgets quotes; coerce to str.
    if password is None:
        raise ConfigError("'database.password' must not be null.")
    password = str(password)

    return DatabaseConfig(
        host=host.strip(),
        port=port,
        dbname=dbname.strip(),
        username=username.strip(),
        password=password,
    )


def _parse_tables(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        raise ConfigError("'tables' must be a list of table name strings.")
    if not raw:
        raise ConfigError("'tables' must contain at least one table name.")

    tables: list[str] = []
    for idx, item in enumerate(raw):
        if not isinstance(item, str) or not item.strip():
            raise ConfigError(
                f"'tables[{idx}]' must be a non-empty string, got {item!r}."
            )
        tables.append(item.strip())

    return tables


def _parse_retry(raw: Any) -> RetryConfig:
    """Parse optional retry block; returns defaults when *raw* is None."""
    if raw is None:
        return RetryConfig()

    if not isinstance(raw, dict):
        raise ConfigError("'retry' must be a mapping.")

    defaults = RetryConfig()
    max_retries = raw.get("max_retries", defaults.max_retries)
    backoff_factor = raw.get("backoff_factor", defaults.backoff_factor)

    if not isinstance(max_retries, int) or isinstance(max_retries, bool):
        raise ConfigError("'retry.max_retries' must be an integer.")
    if max_retries < 0:
        raise ConfigError("'retry.max_retries' must be >= 0.")

    if not isinstance(backoff_factor, (int, float)) or isinstance(backoff_factor, bool):
        raise ConfigError("'retry.backoff_factor' must be a number.")
    if backoff_factor < 0:
        raise ConfigError("'retry.backoff_factor' must be >= 0.")

    return RetryConfig(max_retries=max_retries, backoff_factor=float(backoff_factor))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_config(path: str | Path) -> AppConfig:
    """Load and validate the YAML config file at *path*.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        A fully-validated :class:`AppConfig` instance.

    Raises:
        FileNotFoundError: If *path* does not exist.
        ConfigError: If the file is invalid or missing required fields.
        yaml.YAMLError: If the file is not valid YAML.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    if not isinstance(raw, dict):
        raise ConfigError("Config file must contain a YAML mapping at the top level.")

    database = _parse_database(raw.get("database"))
    tables = _parse_tables(raw.get("tables"))
    retry = _parse_retry(raw.get("retry"))

    return AppConfig(database=database, tables=tables, retry=retry)


# ---------------------------------------------------------------------------
# CLI entry point (for quick manual testing)
# ---------------------------------------------------------------------------


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Parse and display a sync config file.")
    parser.add_argument("config", help="Path to the YAML config file.")
    args = parser.parse_args()

    try:
        cfg = load_config(args.config)
    except (FileNotFoundError, ConfigError, yaml.YAMLError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Database:")
    print(f"  host         : {cfg.database.host}")
    print(f"  port         : {cfg.database.port}")
    print(f"  dbname       : {cfg.database.dbname}")
    print(f"  username     : {cfg.database.username}")
    print(f"  password     : {'*' * len(cfg.database.password)}")
    print(f"\nTables ({len(cfg.tables)}):")
    for table in cfg.tables:
        print(f"  - {table}")
    print("\nRetry settings:")
    print(f"  max_retries  : {cfg.retry.max_retries}")
    print(f"  backoff_factor: {cfg.retry.backoff_factor}")


if __name__ == "__main__":
    main()
