"""
Reusable constrained types for Pydantic models.

Each type is defined as an Annotated alias combining a base type with
one or more validator/constraint annotations. This keeps validation
logic co-located with the type definition and makes every type
reusable across any number of models just by importing it.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    Field,
    HttpUrl,
    field_validator,
)
from pydantic.functional_validators import BeforeValidator


# ---------------------------------------------------------------------------
# Primitive constrained types
# ---------------------------------------------------------------------------

# A whole number that is strictly greater than zero.
PositiveInt = Annotated[int, Field(gt=0)]

# A string that contains at least one character after stripping whitespace.
NonEmptyString = Annotated[str, Field(min_length=1), AfterValidator(str.strip)]


def _validate_email(value: str) -> str:
    """Minimal RFC-5321-style e-mail validator (no external library required)."""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.fullmatch(pattern, value):
        raise ValueError(f"{value!r} is not a valid email address")
    return value.lower()


# An e-mail address (case-normalised to lowercase).
EmailAddress = Annotated[str, AfterValidator(_validate_email)]


def _validate_money(value: Decimal) -> Decimal:
    """Ensure the value is positive and has at most two decimal places."""
    if value <= 0:
        raise ValueError("Money amount must be positive")
    # quantize to 2dp and compare – if they differ the input had more places.
    quantized = value.quantize(Decimal("0.01"))
    if quantized != value:
        raise ValueError("Money amount must have at most 2 decimal places")
    return quantized


# A positive monetary amount with exactly two decimal places.
# Accept str/float/int as input so callers can write MoneyAmount = "9.99".
MoneyAmount = Annotated[
    Decimal,
    BeforeValidator(lambda v: Decimal(str(v)) if not isinstance(v, Decimal) else v),
    AfterValidator(_validate_money),
]


def _validate_percentage(value: float) -> float:
    if not (0.0 <= value <= 100.0):
        raise ValueError(f"Percentage must be between 0 and 100, got {value}")
    return value


# A percentage value in the closed interval [0, 100].
Percentage = Annotated[float, AfterValidator(_validate_percentage)]


def _validate_https_url(value: str) -> str:
    """Reject any URL whose scheme is not https."""
    if not value.startswith("https://"):
        raise ValueError(f"URL must use the https scheme, got: {value!r}")
    return value


# An HTTP URL that is restricted to the https scheme.
# Pydantic's HttpUrl already validates structure; we add the scheme check.
HttpsUrl = Annotated[HttpUrl, AfterValidator(lambda v: _validate_https_url(str(v)))]


# ---------------------------------------------------------------------------
# Example model that uses all constrained types
# ---------------------------------------------------------------------------

class ProductListing(BaseModel):
    """Demonstrates every constrained type defined above."""

    id: PositiveInt
    name: NonEmptyString
    seller_email: EmailAddress
    price: MoneyAmount
    discount_percent: Percentage
    product_url: HttpsUrl

    # Optional: show that model_config can tighten things further
    model_config = {"str_strip_whitespace": True}


# ---------------------------------------------------------------------------
# Quick smoke-test / usage demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # --- valid listing ---
    listing = ProductListing(
        id=42,
        name="Wireless Headphones",
        seller_email="Seller@Example.COM",   # will be lowercased
        price="149.99",                       # str accepted, converted to Decimal
        discount_percent=15.0,
        product_url="https://shop.example.com/headphones",
    )
    print("Valid listing:")
    print(listing.model_dump())
    print()

    # --- demonstrate validation errors ---
    from pydantic import ValidationError

    bad_cases: list[tuple[str, dict]] = [
        (
            "negative id",
            dict(
                id=-1,
                name="Item",
                seller_email="a@b.com",
                price="10.00",
                discount_percent=0,
                product_url="https://example.com",
            ),
        ),
        (
            "empty name",
            dict(
                id=1,
                name="   ",
                seller_email="a@b.com",
                price="10.00",
                discount_percent=0,
                product_url="https://example.com",
            ),
        ),
        (
            "bad email",
            dict(
                id=1,
                name="Item",
                seller_email="not-an-email",
                price="10.00",
                discount_percent=0,
                product_url="https://example.com",
            ),
        ),
        (
            "too many decimal places",
            dict(
                id=1,
                name="Item",
                seller_email="a@b.com",
                price="10.999",
                discount_percent=0,
                product_url="https://example.com",
            ),
        ),
        (
            "percentage > 100",
            dict(
                id=1,
                name="Item",
                seller_email="a@b.com",
                price="10.00",
                discount_percent=101,
                product_url="https://example.com",
            ),
        ),
        (
            "http not https",
            dict(
                id=1,
                name="Item",
                seller_email="a@b.com",
                price="10.00",
                discount_percent=0,
                product_url="http://example.com",
            ),
        ),
    ]

    for label, data in bad_cases:
        try:
            ProductListing(**data)
            print(f"UNEXPECTED PASS for: {label}")
        except ValidationError as exc:
            errors = [e["msg"] for e in exc.errors()]
            print(f"Expected error ({label}): {errors}")
