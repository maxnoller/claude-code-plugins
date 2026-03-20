from __future__ import annotations

from pathlib import Path
from typing import Annotated

import yaml
from pydantic import BaseModel, ConfigDict, Field


# Reusable constrained types — defined once, used everywhere
NonEmptyStr = Annotated[str, Field(min_length=1)]
PositiveInt = Annotated[int, Field(gt=0)]
ValidPort = Annotated[int, Field(ge=1, le=65535)]
PositiveFloat = Annotated[float, Field(gt=0.0)]


class DatabaseConfig(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    host: NonEmptyStr
    port: ValidPort
    dbname: NonEmptyStr
    username: NonEmptyStr
    password: NonEmptyStr


class RetryConfig(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    max_retries: PositiveInt = 3
    backoff_factor: PositiveFloat = 0.5


class AppConfig(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    database: DatabaseConfig
    tables: Annotated[list[NonEmptyStr], Field(min_length=1)]
    retry: RetryConfig = Field(default_factory=RetryConfig)


def load_config(path: Path) -> AppConfig:
    raw = yaml.safe_load(path.read_text())
    return AppConfig.model_validate(raw)
