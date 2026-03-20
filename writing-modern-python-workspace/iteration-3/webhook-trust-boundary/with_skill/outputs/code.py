from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

# Reusable constrained types — define once, import everywhere
NonEmptyStr = Annotated[str, Field(min_length=1)]
PositiveInt = Annotated[int, Field(gt=0)]


class Customer(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    id: NonEmptyStr
    email: NonEmptyStr
    name: NonEmptyStr


class StripeWebhookPayload(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    event_type: NonEmptyStr
    timestamp: datetime
    amount_cents: PositiveInt
    currency: NonEmptyStr
    customer: Customer


app = FastAPI()


@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request) -> dict[str, str]:
    body = await request.json()

    try:
        payload = StripeWebhookPayload.model_validate(body)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # payload is validated and immutable — safe to pass downstream
    return {"status": "ok", "event_type": payload.event_type}
