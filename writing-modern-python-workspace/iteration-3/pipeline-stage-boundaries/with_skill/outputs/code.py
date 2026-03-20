"""
Pipeline stage boundary models.

Each stage boundary uses Pydantic with strict=True, frozen=True, extra="forbid".
This catches type mismatches at the seam, prevents mutation after validation,
and rejects unknown fields from stale producers.

Internal helpers (e.g. the stage functions themselves) use plain dataclasses —
no validation overhead where our own code is the producer.
"""

from __future__ import annotations

import csv
import io
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Shared constrained types — define once, import everywhere
# ---------------------------------------------------------------------------

NonEmptyStr = Annotated[str, Field(min_length=1)]
PositiveDecimal = Annotated[Decimal, Field(gt=0)]
NullableStr = Annotated[str | None, Field(default=None)]


# ---------------------------------------------------------------------------
# Stage 1 → Stage 2: cleaned records from CSV
# ---------------------------------------------------------------------------

class CleanedRecord(BaseModel):
    """Output of Stage 1 (CSV reader + cleaner). Input to Stage 2 (enricher)."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    # Identity
    record_id: NonEmptyStr
    source_file: NonEmptyStr

    # Customer fields
    customer_id: NonEmptyStr
    customer_name: NonEmptyStr
    customer_email: NonEmptyStr
    customer_country: NonEmptyStr  # ISO 3166-1 alpha-2

    # Order fields
    order_date: date
    order_reference: NonEmptyStr
    line_item_count: int
    unit_price: PositiveDecimal
    quantity: int
    total_amount: PositiveDecimal

    # Metadata
    raw_row_number: int
    ingested_at: datetime


# ---------------------------------------------------------------------------
# Stage 2 → Stage 3: enriched records with API data appended
# ---------------------------------------------------------------------------

class EnrichedRecord(BaseModel):
    """Output of Stage 2 (API enricher). Input to Stage 3 (DB writer)."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    # All cleaned fields carried forward — use model_copy on CleanedRecord
    # and add enrichment fields rather than repeating every field.
    # Composition via a nested model keeps both boundaries independently typed.
    cleaned: CleanedRecord

    # Enrichment from external API
    customer_tier: NonEmptyStr           # e.g. "gold", "silver", "bronze"
    customer_lifetime_value: PositiveDecimal
    tax_rate: Decimal                    # may be 0.0, so not PositiveDecimal
    tax_amount: Decimal
    currency_code: NonEmptyStr           # ISO 4217
    exchange_rate_to_usd: PositiveDecimal

    # API metadata
    enriched_at: datetime
    api_request_id: NonEmptyStr
    api_latency_ms: NullableStr          # present when debug mode on, else None


# ---------------------------------------------------------------------------
# Stage functions (internal — plain Python, no Pydantic overhead)
# ---------------------------------------------------------------------------

def stage1_read_csv(csv_text: str, source_file: str) -> list[CleanedRecord]:
    """Read and clean CSV rows; validate at stage exit with Pydantic."""
    reader = csv.DictReader(io.StringIO(csv_text))
    records: list[CleanedRecord] = []
    for row_number, row in enumerate(reader, start=2):  # 1-indexed, row 1 = header
        records.append(
            CleanedRecord(
                record_id=f"{source_file}:{row_number}",
                source_file=source_file,
                customer_id=row["customer_id"].strip(),
                customer_name=row["customer_name"].strip(),
                customer_email=row["customer_email"].strip().lower(),
                customer_country=row["customer_country"].strip().upper(),
                order_date=date.fromisoformat(row["order_date"].strip()),
                order_reference=row["order_reference"].strip(),
                line_item_count=int(row["line_item_count"]),
                unit_price=Decimal(row["unit_price"].strip()),
                quantity=int(row["quantity"]),
                total_amount=Decimal(row["total_amount"].strip()),
                raw_row_number=row_number,
                ingested_at=datetime.now(),  # noqa: DTZ005
            )
        )
    return records


def stage2_enrich(cleaned: CleanedRecord, api_response: dict) -> EnrichedRecord:
    """Wrap a cleaned record with API enrichment data; validate at stage exit."""
    return EnrichedRecord(
        cleaned=cleaned,
        customer_tier=api_response["tier"],
        customer_lifetime_value=Decimal(str(api_response["lifetime_value"])),
        tax_rate=Decimal(str(api_response["tax_rate"])),
        tax_amount=Decimal(str(api_response["tax_amount"])),
        currency_code=api_response["currency_code"],
        exchange_rate_to_usd=Decimal(str(api_response["exchange_rate_to_usd"])),
        enriched_at=datetime.now(),  # noqa: DTZ005
        api_request_id=api_response["request_id"],
        api_latency_ms=api_response.get("latency_ms"),
    )


def stage3_write_to_db(records: list[EnrichedRecord]) -> None:
    """Write enriched records to the database.

    At this boundary the data is already validated — access fields directly
    without re-validation. Use record.cleaned.* for original CSV fields.
    """
    for record in records:
        row = {
            # Identity / metadata
            "record_id": record.cleaned.record_id,
            "source_file": record.cleaned.source_file,
            "raw_row_number": record.cleaned.raw_row_number,
            "ingested_at": record.cleaned.ingested_at.isoformat(),
            "enriched_at": record.enriched_at.isoformat(),
            # Customer
            "customer_id": record.cleaned.customer_id,
            "customer_name": record.cleaned.customer_name,
            "customer_email": record.cleaned.customer_email,
            "customer_country": record.cleaned.customer_country,
            "customer_tier": record.customer_tier,
            "customer_lifetime_value": str(record.customer_lifetime_value),
            # Order
            "order_date": record.cleaned.order_date.isoformat(),
            "order_reference": record.cleaned.order_reference,
            "line_item_count": record.cleaned.line_item_count,
            "unit_price": str(record.cleaned.unit_price),
            "quantity": record.cleaned.quantity,
            "total_amount": str(record.cleaned.total_amount),
            # Financials from API
            "tax_rate": str(record.tax_rate),
            "tax_amount": str(record.tax_amount),
            "currency_code": record.currency_code,
            "exchange_rate_to_usd": str(record.exchange_rate_to_usd),
            # API metadata
            "api_request_id": record.api_request_id,
            "api_latency_ms": record.api_latency_ms,
        }
        # db.execute("INSERT INTO orders ...", row)  # plug in your DB layer here
        _ = row  # placeholder


# ---------------------------------------------------------------------------
# Usage example
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample_csv = """\
customer_id,customer_name,customer_email,customer_country,order_date,order_reference,line_item_count,unit_price,quantity,total_amount
C001,Alice Smith,alice@example.com,US,2026-03-01,ORD-9001,3,29.99,2,59.98
"""

    sample_api_response = {
        "tier": "gold",
        "lifetime_value": "4250.00",
        "tax_rate": "0.08",
        "tax_amount": "4.80",
        "currency_code": "USD",
        "exchange_rate_to_usd": "1.0",
        "request_id": "req-abc123",
        "latency_ms": None,
    }

    cleaned_records = stage1_read_csv(sample_csv, source_file="orders_2026_03.csv")
    enriched_records = [stage2_enrich(r, sample_api_response) for r in cleaned_records]
    stage3_write_to_db(enriched_records)

    print(f"Processed {len(enriched_records)} record(s).")
    print(enriched_records[0].model_dump())
