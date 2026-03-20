from __future__ import annotations

from datetime import datetime
from enum import Enum

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------


class EventType(str, Enum):
    payment_intent_succeeded = "payment_intent.succeeded"
    payment_intent_payment_failed = "payment_intent.payment_failed"
    charge_succeeded = "charge.succeeded"
    charge_failed = "charge.failed"
    customer_subscription_created = "customer.subscription.created"
    customer_subscription_updated = "customer.subscription.updated"
    customer_subscription_deleted = "customer.subscription.deleted"
    invoice_payment_succeeded = "invoice.payment_succeeded"
    invoice_payment_failed = "invoice.payment_failed"


# ISO 4217 subset — extend as needed
SUPPORTED_CURRENCIES = frozenset(
    {
        "usd", "eur", "gbp", "cad", "aud", "jpy", "chf",
        "sek", "nok", "dkk", "nzd", "sgd", "hkd",
    }
)


class Customer(BaseModel):
    id: str = Field(..., min_length=1, max_length=255, description="Stripe customer ID")
    email: str | None = Field(
        default=None,
        max_length=254,
        description="Customer email address",
    )
    name: str | None = Field(default=None, max_length=512, description="Customer display name")

    @field_validator("id")
    @classmethod
    def id_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("customer.id must not be blank or whitespace")
        return v

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        # Basic structural check — use `email-validator` for production
        if "@" not in v or v.startswith("@") or v.endswith("@"):
            raise ValueError(f"customer.email '{v}' does not look like a valid address")
        return v.lower().strip()


class StripeWebhookPayload(BaseModel):
    event_type: EventType = Field(..., description="Stripe event type string")
    timestamp: datetime = Field(
        ...,
        description="ISO-8601 UTC timestamp of the event",
    )
    amount_cents: int = Field(
        ...,
        ge=0,
        le=99_999_999,  # ~$1 M — adjust to your business rules
        description="Amount in the smallest currency unit (cents, pence, etc.)",
    )
    currency: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    customer: Customer = Field(..., description="Nested customer object")

    @field_validator("currency")
    @classmethod
    def currency_must_be_supported(cls, v: str) -> str:
        normalised = v.lower().strip()
        if normalised not in SUPPORTED_CURRENCIES:
            raise ValueError(
                f"currency '{v}' is not in the supported set: "
                f"{sorted(SUPPORTED_CURRENCIES)}"
            )
        return normalised

    @model_validator(mode="after")
    def zero_amount_only_for_certain_events(self) -> "StripeWebhookPayload":
        """
        Zero-amount events are only meaningful for subscription lifecycle events.
        Reject a zero amount on charge / payment-intent events to catch mis-routed
        or replayed payloads early.
        """
        zero_amount_allowed_events = {
            EventType.customer_subscription_created,
            EventType.customer_subscription_updated,
            EventType.customer_subscription_deleted,
        }
        if self.amount_cents == 0 and self.event_type not in zero_amount_allowed_events:
            raise ValueError(
                f"amount_cents cannot be 0 for event_type '{self.event_type}'"
            )
        return self


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(title="Stripe Webhook Receiver", version="1.0.0")


@app.post(
    "/webhooks/stripe",
    status_code=status.HTTP_200_OK,
    summary="Receive and validate Stripe webhook events",
)
async def receive_stripe_webhook(request: Request) -> dict[str, str]:
    """
    Accepts a JSON webhook from Stripe.

    Rejects malformed payloads with 422 Unprocessable Entity. Returns 200 OK
    with a brief acknowledgement on success so Stripe stops retrying.

    NOTE: In production you MUST also verify the ``Stripe-Signature`` header
    using ``stripe.WebhookSignature.verify_header`` (or the ``stripe`` SDK's
    ``stripe.Webhook.construct_event``). That step is omitted here because it
    requires the signing secret and the raw request body before JSON parsing.
    """
    raw_body: bytes = await request.body()

    if not raw_body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body is empty",
        )

    # Parse and validate via Pydantic — raises RequestValidationError on
    # failure, which FastAPI automatically converts to a 422 response with a
    # structured JSON body describing every field-level error.
    try:
        import json as _json

        data = _json.loads(raw_body)
    except _json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request body is not valid JSON: {exc}",
        ) from exc

    # Let Pydantic do the heavy lifting; unhandled ValidationError propagates
    # as a 422 via FastAPI's default exception handler.
    payload = StripeWebhookPayload.model_validate(data)

    # --------------------------------------------------------------------
    # Business logic goes here — hand off to a service layer, enqueue a job,
    # emit a domain event, etc.
    # --------------------------------------------------------------------
    _handle_event(payload)

    return {"status": "received", "event_type": payload.event_type.value}


def _handle_event(payload: StripeWebhookPayload) -> None:
    """
    Stub dispatcher.  Replace with real routing logic.
    """
    handlers = {
        EventType.payment_intent_succeeded: _on_payment_succeeded,
        EventType.charge_failed: _on_charge_failed,
    }
    handler = handlers.get(payload.event_type)
    if handler:
        handler(payload)


def _on_payment_succeeded(payload: StripeWebhookPayload) -> None:
    # Fulfil order, send receipt email, etc.
    pass


def _on_charge_failed(payload: StripeWebhookPayload) -> None:
    # Notify customer, retry logic, etc.
    pass
