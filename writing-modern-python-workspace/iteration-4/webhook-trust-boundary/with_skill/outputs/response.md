```python
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

# Reusable constrained types
NonEmptyStr = Annotated[str, Field(min_length=1)]
PositiveInt = Annotated[int, Field(gt=0)]


class Customer(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    id: NonEmptyStr
    email: str = Field(pattern=r"^[^@]+@[^@]+\.[^@]+$")
    name: NonEmptyStr | None = None


class StripeWebhookPayload(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    event_type: NonEmptyStr
    timestamp: datetime
    amount_cents: PositiveInt
    currency: Annotated[str, Field(min_length=3, max_length=3)]
    customer: Customer


app = FastAPI()


@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request) -> dict:
    body = await request.json()
    try:
        payload = StripeWebhookPayload.model_validate(body)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=e.errors()) from e

    # payload is validated and immutable here
    match payload.event_type:
        case "payment_intent.succeeded":
            ...
        case "payment_intent.payment_failed":
            ...

    return {"status": "accepted"}
```

A few decisions worth noting:

**`strict=True`** — Stripe sends `amount_cents` as an integer, but without strict mode Pydantic silently coerces `"500"` (string) to `500`. Strict mode rejects that, so a malformed payload fails validation rather than sneaking through.

**`extra="forbid"`** — rejects payloads with unknown fields. This catches payload version drift early (Stripe adding fields you haven't accounted for) rather than silently ignoring them.

**`frozen=True`** — once validated, the payload can't be mutated anywhere in your handler chain.

**Trust boundary placement** — validate once at the endpoint, then pass `payload` around internally as a trusted object. Don't re-validate it in downstream functions.

For real Stripe webhooks you'll also want to verify the `Stripe-Signature` header before parsing the body — Stripe's SDK does this with `stripe.Webhook.construct_event(raw_body, sig_header, secret)`. Do that check *before* calling `model_validate`, since the signature check requires the raw bytes.
