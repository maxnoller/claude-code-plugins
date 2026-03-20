from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

NonEmptyStr = Annotated[str, Field(min_length=1)]


class SensorReading(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    sensor_id: NonEmptyStr
    value: float
    timestamp: datetime
    metadata: dict[str, object] | None = None


# Instantiate once at module level — construction cost is paid here, not per message.
# TypeAdapter[list[SensorReading]] validates a JSON array without wrapping it in a
# container model, which avoids the overhead of an extra BaseModel layer in the hot loop.
_readings_adapter: TypeAdapter[list[SensorReading]] = TypeAdapter(list[SensorReading])


def validate_sensor_readings(data: bytes) -> list[SensorReading]:
    """Validate raw JSON bytes from the message queue as a list of SensorReadings.

    Uses model_validate_json() via TypeAdapter for a single Rust-level parse-and-validate
    pass — faster than json.loads() followed by model_validate().

    Raises ValidationError if the payload is invalid.
    """
    return _readings_adapter.validate_json(data)
