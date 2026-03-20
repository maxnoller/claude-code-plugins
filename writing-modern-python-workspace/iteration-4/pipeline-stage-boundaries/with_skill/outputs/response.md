Two trust boundaries exist in your pipeline: the CSV input and the API response. Validate there with Pydantic. Everything flowing *between* your own stages is already validated data — use `dataclass` there.

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field

# ── Shared constrained types ──────────────────────────────────────────────────
NonEmptyStr = Annotated[str, Field(min_length=1)]
PositiveFloat = Annotated[float, Field(gt=0)]

# ── Stage 1: Trust boundary — raw CSV input ───────────────────────────────────
class RawRecord(BaseModel):
    """Validates CSV rows. Pydantic because this is external, untrusted input."""
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    customer_id: NonEmptyStr
    email: NonEmptyStr
    amount: PositiveFloat
    currency: NonEmptyStr
    transaction_date: datetime
    # ... 10 more fields

# ── Stage 2: Trust boundary — API response ────────────────────────────────────
class ApiEnrichment(BaseModel):
    """Validates the enrichment API response shape."""
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    risk_score: float
    country_code: str
    is_flagged: bool

# ── Internal record flowing between stages ────────────────────────────────────
@dataclass(frozen=True)
class EnrichedRecord:
    """Plain dataclass — data is already validated, no need for Pydantic overhead."""
    customer_id: str
    email: str
    amount: float
    currency: str
    transaction_date: datetime
    risk_score: float
    country_code: str
    is_flagged: bool
    # ... remaining fields

# ── Stage functions ───────────────────────────────────────────────────────────
def stage1_clean(rows: list[dict]) -> list[EnrichedRecord]:
    validated = [RawRecord.model_validate(row) for row in rows]
    return [EnrichedRecord(
        customer_id=r.customer_id,
        email=r.email,
        amount=r.amount,
        # ... map fields, transform as needed
        risk_score=0.0,       # placeholder until stage 2 fills it
        country_code="",
        is_flagged=False,
    ) for r in validated]

def stage2_enrich(records: list[EnrichedRecord], api_client) -> list[EnrichedRecord]:
    enriched = []
    for record in records:
        raw = api_client.get_enrichment(record.customer_id)
        api_data = ApiEnrichment.model_validate(raw)  # trust boundary again
        enriched.append(EnrichedRecord(
            **{**record.__dict__,
               "risk_score": api_data.risk_score,
               "country_code": api_data.country_code,
               "is_flagged": api_data.is_flagged,
            }
        ))
    return enriched

def stage3_write(records: list[EnrichedRecord], db) -> None:
    # No validation needed — data is trusted at this point
    db.bulk_insert([r.__dict__ for r in records])
```

**The decision rule:** Pydantic where data enters from outside your code (CSV files, API responses, user input, message queues). Plain `dataclass` for data your own code produces and passes internally — once it's validated, trust it.

**Why not Pydantic throughout?** Pydantic has validation overhead and signals "this is an untrusted boundary" to readers. Using it for internal handoffs is misleading and wastes cycles. `frozen=True` on the dataclass gives you the same immutability guarantee without the overhead.

**One alternative:** if Stage 1 and Stage 2 produce meaningfully different shapes (not just added fields), consider two separate dataclasses — `CleanedRecord` and `EnrichedRecord`. If stage 2 just adds fields, a single dataclass with optional fields is fine.
