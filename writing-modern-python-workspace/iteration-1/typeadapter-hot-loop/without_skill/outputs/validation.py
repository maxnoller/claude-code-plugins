"""
Validation of sensor reading messages from a message queue.

Optimized for high-throughput hot loops: uses a module-level TypeAdapter
instance to avoid repeated model rebuilding on every call.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, TypeAdapter


class SensorReading(BaseModel):
    sensor_id: str
    value: float
    timestamp: datetime
    metadata: dict[str, Any] | None = None


# Build the TypeAdapter once at module level so it is not re-created on each
# call.  TypeAdapter construction is expensive; reusing the same instance is
# the key optimisation for hot-loop scenarios.
_readings_adapter: TypeAdapter[list[SensorReading]] = TypeAdapter(
    list[SensorReading]
)


def validate_sensor_readings(raw: bytes) -> list[SensorReading]:
    """Parse and validate a JSON-encoded list of sensor readings.

    Parameters
    ----------
    raw:
        Raw bytes received from the message queue.  Must be a JSON array
        whose elements each conform to the SensorReading schema.

    Returns
    -------
    list[SensorReading]
        Validated list of sensor reading objects.

    Raises
    ------
    json.JSONDecodeError
        If *raw* is not valid JSON.
    pydantic.ValidationError
        If the decoded data does not match the expected schema.
    """
    # validate_json accepts bytes directly, skipping an intermediate Python
    # object and avoiding a redundant json.loads() call.
    return _readings_adapter.validate_json(raw)


# ---------------------------------------------------------------------------
# Example usage / quick smoke-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample: bytes = json.dumps(
        [
            {
                "sensor_id": "temp-01",
                "value": 23.4,
                "timestamp": "2026-03-20T12:00:00Z",
                "metadata": {"unit": "celsius", "location": "room-A"},
            },
            {
                "sensor_id": "pressure-07",
                "value": 1013.25,
                "timestamp": "2026-03-20T12:00:01Z",
            },
        ]
    ).encode()

    readings = validate_sensor_readings(sample)
    for r in readings:
        print(r)
