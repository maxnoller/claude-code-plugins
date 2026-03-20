from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Reusable constrained types
# ---------------------------------------------------------------------------

NonEmptyStr = Annotated[str, Field(min_length=1)]
AmountCents = Annotated[int, Field(ge=0, description="Amount in cents")]
CurrencyCode = Annotated[str, Field(min_length=3, max_length=3, description="ISO 4217 currency code")]
CustomerId = Annotated[str, Field(min_length=1)]
Email = Annotated[str, Field(pattern=r"^[\w.+-]+@[\w.-]+\.\w+$")]


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------

class Customer(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    id: CustomerId
    email: Email
    name: str | None = None


class LineItem(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    description: NonEmptyStr
    amount: AmountCents
    currency: CurrencyCode
    quantity: Annotated[int, Field(gt=0)] = 1


# ---------------------------------------------------------------------------
# Discriminated event data variants
# ---------------------------------------------------------------------------

class InvoiceData(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    event_type: Literal["invoice.paid", "invoice.payment_failed", "invoice.created"]
    line_items: Annotated[list[LineItem], Field(min_length=1)]


class ChargeData(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    event_type: Literal["charge.succeeded", "charge.failed", "charge.refunded"]
    payment_method: NonEmptyStr


# ---------------------------------------------------------------------------
# Top-level webhook payload — discriminated union on event_type
# ---------------------------------------------------------------------------

StripeEventData = Annotated[
    InvoiceData | ChargeData,
    Field(discriminator="event_type"),
]


class StripeWebhookPayload(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    event_type: NonEmptyStr
    timestamp: datetime
    amount: AmountCents
    currency: CurrencyCode
    customer: Customer
    data: StripeEventData
