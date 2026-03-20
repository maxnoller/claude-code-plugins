Config files are a trust boundary (external input you don't control), so Pydantic is the right call here.

```bash
uv add pydantic pyyaml
```

```python
# config.py
from pathlib import Path
from typing import Annotated

import yaml
from pydantic import BaseModel, ConfigDict, Field

NonEmptyStr = Annotated[str, Field(min_length=1)]
PositiveInt = Annotated[int, Field(gt=0)]


class DatabaseConfig(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    host: NonEmptyStr
    port: PositiveInt
    dbname: NonEmptyStr
    username: NonEmptyStr
    password: NonEmptyStr


class RetryConfig(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    max_retries: Annotated[int, Field(ge=0)] = 3
    backoff_factor: Annotated[float, Field(gt=0)] = 0.5


class AppConfig(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    database: DatabaseConfig
    tables: Annotated[list[NonEmptyStr], Field(min_length=1)]
    retry: RetryConfig = RetryConfig()


def load_config(path: Path) -> AppConfig:
    raw = yaml.safe_load(path.read_text())
    return AppConfig.model_validate(raw)
```

Example config that validates against this:

```yaml
# config.yaml
database:
  host: localhost
  port: 5432
  dbname: mydb
  username: alice
  password: secret

tables:
  - orders
  - customers

retry:
  max_retries: 5
  backoff_factor: 1.5
```

Usage in your CLI:

```python
import sys
from pathlib import Path
from pydantic import ValidationError

config_path = Path(sys.argv[1])
try:
    config = load_config(config_path)
except FileNotFoundError:
    sys.exit(f"Config file not found: {config_path}")
except yaml.YAMLError as e:
    sys.exit(f"Invalid YAML: {e}")
except ValidationError as e:
    sys.exit(f"Config validation failed:\n{e}")
```

A few design decisions worth noting:

- **`strict=True`** — prevents silent coercion. Without it, Pydantic would happily accept `port: "5432"` (string) as an int. With it, you get an explicit error pointing at the bad field.
- **`frozen=True`** — config is read-once at startup; immutability prevents accidental mutation downstream.
- **`retry: RetryConfig = RetryConfig()`** — the entire retry block is optional, defaulting to sensible values. Don't make users specify it unless they want to override.
- **`tables: list[NonEmptyStr]` with `min_length=1`** — rejects an empty list, since syncing zero tables is almost certainly a misconfiguration.
