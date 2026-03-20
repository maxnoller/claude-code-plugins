"""
Data pipeline with typed stage boundaries using dataclasses.

Each stage produces and consumes well-defined types, making the data flow
explicit and checkable. Using dataclasses with frozen=True keeps records
immutable between stages, preventing accidental mutation.
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass, field, replace
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, auto
from typing import Iterator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared enumerations
# ---------------------------------------------------------------------------


class CustomerTier(str, Enum):
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class RecordStatus(Enum):
    PENDING = auto()
    ENRICHED = auto()
    WRITTEN = auto()


# ---------------------------------------------------------------------------
# Stage 1 output: CleanedRecord
# Produced by: read_csv()
# Consumed by: enrich_record()
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CleanedRecord:
    """A record after CSV ingestion and basic cleaning/validation.

    All fields use appropriate Python types (not raw strings), so downstream
    stages can rely on the types without re-parsing.
    """

    # Identity
    record_id: str
    source_file: str

    # Customer info
    customer_id: str
    customer_name: str
    customer_email: str
    customer_tier: CustomerTier

    # Order info
    order_date: date
    order_reference: str
    line_item_count: int
    gross_amount: Decimal
    currency: str  # ISO 4217, e.g. "USD"

    # Product info
    product_sku: str
    product_category: str

    # Metadata
    raw_row_number: int
    ingested_at: datetime = field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Stage 2 output: EnrichedRecord
# Produced by: enrich_record()
# Consumed by: write_to_database()
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EnrichedRecord:
    """A CleanedRecord augmented with data fetched from external APIs.

    Carries the original CleanedRecord unchanged so the database writer can
    access any field from either stage without an impedance mismatch.
    """

    # Original cleaned record — fully preserved
    cleaned: CleanedRecord

    # Customer enrichment (from CRM API)
    customer_country: str
    customer_region: str
    account_manager: str
    contract_start_date: date | None

    # Product enrichment (from product catalogue API)
    product_name: str
    product_weight_kg: Decimal | None
    product_is_hazardous: bool

    # Financial enrichment (from FX rates API)
    exchange_rate_to_usd: Decimal
    amount_usd: Decimal

    # Metadata
    enriched_at: datetime = field(default_factory=datetime.utcnow)
    status: RecordStatus = RecordStatus.ENRICHED


# ---------------------------------------------------------------------------
# Stage 3 output: WriteResult
# Produced by: write_to_database()
# Consumed by: pipeline orchestrator / reporting
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WriteResult:
    """Confirmation that a record was persisted to the database."""

    record_id: str
    database_pk: int
    written_at: datetime = field(default_factory=datetime.utcnow)
    status: RecordStatus = RecordStatus.WRITTEN


# ---------------------------------------------------------------------------
# Stage 1: CSV reader → CleanedRecord
# ---------------------------------------------------------------------------


def read_csv(filepath: str) -> Iterator[CleanedRecord]:
    """Read a CSV file and yield CleanedRecord instances.

    Raises ValueError for rows that fail validation so the caller can decide
    whether to skip, collect errors, or abort.
    """
    with open(filepath, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row_number, row in enumerate(reader, start=2):  # 2: row 1 is header
            try:
                yield _parse_row(row, filepath, row_number)
            except (ValueError, KeyError) as exc:
                logger.warning("Skipping row %d in %s: %s", row_number, filepath, exc)


def _parse_row(row: dict[str, str], source_file: str, row_number: int) -> CleanedRecord:
    return CleanedRecord(
        record_id=_require(row, "record_id"),
        source_file=source_file,
        customer_id=_require(row, "customer_id"),
        customer_name=_require(row, "customer_name").strip(),
        customer_email=_require(row, "customer_email").lower().strip(),
        customer_tier=CustomerTier(_require(row, "customer_tier")),
        order_date=date.fromisoformat(_require(row, "order_date")),
        order_reference=_require(row, "order_reference"),
        line_item_count=int(_require(row, "line_item_count")),
        gross_amount=Decimal(_require(row, "gross_amount")),
        currency=_require(row, "currency").upper(),
        product_sku=_require(row, "product_sku"),
        product_category=_require(row, "product_category"),
        raw_row_number=row_number,
    )


def _require(row: dict[str, str], key: str) -> str:
    value = row.get(key, "").strip()
    if not value:
        raise ValueError(f"Missing required field: {key!r}")
    return value


# ---------------------------------------------------------------------------
# Stage 2: CleanedRecord → EnrichedRecord
# ---------------------------------------------------------------------------


def enrich_record(record: CleanedRecord, api_client: "ApiClient") -> EnrichedRecord:
    """Call external APIs and return an EnrichedRecord.

    The ApiClient is passed as a dependency so it can be swapped for a stub in
    tests without patching globals.
    """
    customer_data = api_client.get_customer(record.customer_id)
    product_data = api_client.get_product(record.product_sku)
    fx_rate = api_client.get_fx_rate(record.currency, target="USD")

    amount_usd = record.gross_amount * fx_rate

    return EnrichedRecord(
        cleaned=record,
        customer_country=customer_data["country"],
        customer_region=customer_data["region"],
        account_manager=customer_data["account_manager"],
        contract_start_date=(
            date.fromisoformat(customer_data["contract_start"])
            if customer_data.get("contract_start")
            else None
        ),
        product_name=product_data["name"],
        product_weight_kg=(
            Decimal(str(product_data["weight_kg"]))
            if product_data.get("weight_kg") is not None
            else None
        ),
        product_is_hazardous=bool(product_data.get("is_hazardous", False)),
        exchange_rate_to_usd=fx_rate,
        amount_usd=amount_usd,
    )


# ---------------------------------------------------------------------------
# Stage 3: EnrichedRecord → WriteResult
# ---------------------------------------------------------------------------


def write_to_database(record: EnrichedRecord, db: "DatabaseConnection") -> WriteResult:
    """Persist an EnrichedRecord and return a WriteResult.

    Separating the write confirmation into its own type lets the orchestrator
    collect results and report on success/failure without coupling it to the
    record structure.
    """
    pk = db.insert_order(
        record_id=record.cleaned.record_id,
        customer_id=record.cleaned.customer_id,
        customer_country=record.customer_country,
        order_date=record.cleaned.order_date,
        order_reference=record.cleaned.order_reference,
        line_item_count=record.cleaned.line_item_count,
        gross_amount=record.cleaned.gross_amount,
        currency=record.cleaned.currency,
        amount_usd=record.amount_usd,
        product_sku=record.cleaned.product_sku,
        product_name=record.product_name,
        product_category=record.cleaned.product_category,
        customer_tier=record.cleaned.customer_tier.value,
        account_manager=record.account_manager,
        enriched_at=record.enriched_at,
    )
    return WriteResult(record_id=record.cleaned.record_id, database_pk=pk)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def run_pipeline(
    csv_files: list[str],
    api_client: "ApiClient",
    db: "DatabaseConnection",
) -> list[WriteResult]:
    """Tie all three stages together and return write confirmations."""
    results: list[WriteResult] = []
    errors: list[tuple[str, Exception]] = []

    for filepath in csv_files:
        for cleaned in read_csv(filepath):
            try:
                enriched = enrich_record(cleaned, api_client)
                result = write_to_database(enriched, db)
                results.append(result)
                logger.info("Written record %s → db pk %d", result.record_id, result.database_pk)
            except Exception as exc:
                logger.error("Failed to process record %s: %s", cleaned.record_id, exc)
                errors.append((cleaned.record_id, exc))

    logger.info(
        "Pipeline complete: %d written, %d errors",
        len(results),
        len(errors),
    )
    return results


# ---------------------------------------------------------------------------
# Stub interfaces (for documentation / testing)
# ---------------------------------------------------------------------------


class ApiClient:
    """Interface contract expected by enrich_record().

    Replace with a real implementation or a unittest.mock.MagicMock in tests.
    """

    def get_customer(self, customer_id: str) -> dict:
        raise NotImplementedError

    def get_product(self, product_sku: str) -> dict:
        raise NotImplementedError

    def get_fx_rate(self, from_currency: str, target: str) -> Decimal:
        raise NotImplementedError


class DatabaseConnection:
    """Interface contract expected by write_to_database()."""

    def insert_order(self, **kwargs) -> int:
        """Insert a row and return the new primary key."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Example: building an EnrichedRecord in a test without real I/O
# ---------------------------------------------------------------------------


def _example_test_fixture() -> EnrichedRecord:
    """Shows how frozen dataclasses compose cleanly in tests."""
    cleaned = CleanedRecord(
        record_id="REC-001",
        source_file="orders_2026_03.csv",
        customer_id="CUST-42",
        customer_name="Acme Corp",
        customer_email="billing@acme.example",
        customer_tier=CustomerTier.PREMIUM,
        order_date=date(2026, 3, 1),
        order_reference="ORD-20260301-001",
        line_item_count=3,
        gross_amount=Decimal("1500.00"),
        currency="EUR",
        product_sku="WIDGET-XL",
        product_category="hardware",
        raw_row_number=2,
    )

    enriched = EnrichedRecord(
        cleaned=cleaned,
        customer_country="DE",
        customer_region="Europe",
        account_manager="Jane Smith",
        contract_start_date=date(2025, 1, 1),
        product_name="XL Widget",
        product_weight_kg=Decimal("2.5"),
        product_is_hazardous=False,
        exchange_rate_to_usd=Decimal("1.08"),
        amount_usd=Decimal("1620.00"),
    )

    return enriched


if __name__ == "__main__":
    # Demonstrate that the fixture builds without errors
    record = _example_test_fixture()
    print(f"record_id   : {record.cleaned.record_id}")
    print(f"customer    : {record.cleaned.customer_name} ({record.cleaned.customer_tier.value})")
    print(f"order_date  : {record.cleaned.order_date}")
    print(f"gross_amount: {record.cleaned.gross_amount} {record.cleaned.currency}")
    print(f"amount_usd  : {record.amount_usd} USD (rate {record.exchange_rate_to_usd})")
    print(f"product     : {record.product_name} [{record.cleaned.product_sku}]")
    print(f"account_mgr : {record.account_manager}, {record.customer_region}")
