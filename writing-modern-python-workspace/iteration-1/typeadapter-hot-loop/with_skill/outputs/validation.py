from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

NonEmptyStr = Annotated[str, Field(min_length=1)]


class SensorReading(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    sensor_id: NonEmptyStr
    value: float
    timestamp: datetime
    metadata: dict[str, object] | None = None


# TypeAdapter is built once at module level — schema compilation is expensive
# and must never happen inside a hot loop.
_readings_adapter = TypeAdapter(list[SensorReading])


def validate_readings(raw: bytes) -> list[SensorReading]:
    """Parse and validate a JSON message containing a list of sensor readings.

    Uses TypeAdapter.validate_json() for a single Rust-level parse+validate pass,
    avoiding the overhead of json.loads() followed by a separate validation step.
    Raises ValidationError on malformed input.
    """
    return _readings_adapter.validate_json(raw)
