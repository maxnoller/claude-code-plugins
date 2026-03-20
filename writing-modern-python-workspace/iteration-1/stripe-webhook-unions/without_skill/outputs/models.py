from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Union
from pydantic import BaseModel, EmailStr, Field


class Customer(BaseModel):
    id: str
    email: EmailStr
    name: str | None = None


class LineItem(BaseModel):
    description: str
    amount: int  # in cents
    currency: str
    quantity: int = 1


class InvoiceData(BaseModel):
    line_items: list[LineItem]


class ChargeData(BaseModel):
    payment_method: str


class InvoicePaidPayload(BaseModel):
    event_type: Literal["invoice.paid"]
    timestamp: datetime
    amount: int  # in cents
    currency: str
    customer: Customer
    data: InvoiceData


class InvoicePaymentFailedPayload(BaseModel):
    event_type: Literal["invoice.payment_failed"]
    timestamp: datetime
    amount: int  # in cents
    currency: str
    customer: Customer
    data: InvoiceData


class ChargeSucceededPayload(BaseModel):
    event_type: Literal["charge.succeeded"]
    timestamp: datetime
    amount: int  # in cents
    currency: str
    customer: Customer
    data: ChargeData


class ChargeFailedPayload(BaseModel):
    event_type: Literal["charge.failed"]
    timestamp: datetime
    amount: int  # in cents
    currency: str
    customer: Customer
    data: ChargeData


StripeWebhookPayload = Annotated[
    Union[
        InvoicePaidPayload,
        InvoicePaymentFailedPayload,
        ChargeSucceededPayload,
        ChargeFailedPayload,
    ],
    Field(discriminator="event_type"),
]


class StripeWebhookEvent(BaseModel):
    """Top-level wrapper for parsing an incoming Stripe webhook event."""

    payload: StripeWebhookPayload = Field(discriminator="event_type")

    model_config = {"populate_by_name": True}

    @classmethod
    def from_payload(cls, data: dict) -> StripeWebhookPayload:
        """Parse a raw webhook payload dict directly into the correct typed model."""
        return cls.model_validate({"payload": data}).payload
