from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Reusable constrained types
# ---------------------------------------------------------------------------

AmountCents = Annotated[int, Field(ge=0, description="Amount in cents")]
CurrencyCode = Annotated[str, Field(min_length=3, max_length=3, description="ISO 4217 currency code")]
NonEmptyStr = Annotated[str, Field(min_length=1)]

# ---------------------------------------------------------------------------
# Nested objects
# ---------------------------------------------------------------------------


class Customer(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    id: NonEmptyStr
    email: NonEmptyStr
    name: str | None = None


class LineItem(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    description: NonEmptyStr
    amount: AmountCents
    quantity: int = Field(gt=0)


# ---------------------------------------------------------------------------
# Discriminated event data shapes
# ---------------------------------------------------------------------------


class InvoiceData(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    type: Literal["invoice"]
    line_items: list[LineItem]


class ChargeData(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    type: Literal["charge"]
    payment_method: NonEmptyStr


# The discriminated union — O(1) dispatch on the `type` field
EventData = Annotated[Union[InvoiceData, ChargeData], Field(discriminator="type")]

# ---------------------------------------------------------------------------
# Top-level webhook payload
# ---------------------------------------------------------------------------

# Stripe event types are dot-separated "<object>.<action>" strings.
# We derive the data discriminator value from the object prefix so callers
# never have to duplicate that mapping.

_EVENT_TYPE_TO_DATA_TYPE: dict[str, str] = {
    "invoice": "invoice",
    "charge": "charge",
}


class StripeWebhookPayload(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    event_type: NonEmptyStr = Field(
        description="Stripe event type, e.g. 'invoice.paid', 'charge.failed'"
    )
    timestamp: datetime
    amount: AmountCents
    currency: CurrencyCode
    customer: Customer
    data: EventData
