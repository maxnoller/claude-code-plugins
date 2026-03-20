"""Reusable constrained types for use across the codebase.

Define once, import everywhere. Never inline Field constraints repeatedly.
"""

from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Constrained primitives
# ---------------------------------------------------------------------------

PositiveInt = Annotated[int, Field(gt=0)]

NonEmptyStr = Annotated[str, Field(min_length=1)]

Email = Annotated[
    str,
    Field(pattern=r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"),
]

# Money: positive, exactly 2 decimal places.
# AfterValidator rounds to 2dp so the constraint is always met after coercion,
# then Field(ge=...) enforces positivity on the rounded value.
MoneyAmount = Annotated[
    Decimal,
    AfterValidator(lambda v: round(v, 2)),
    Field(gt=Decimal("0.00")),
]

# Percentage: inclusive 0–100, up to 2dp is plenty for any real rate.
Percentage = Annotated[Decimal, Field(ge=Decimal("0"), le=Decimal("100"))]

# URL must use the https scheme; we validate with a simple AfterValidator
# rather than pulling in a URL library, keeping the dependency surface minimal.
def _require_https(url: str) -> str:
    if not url.startswith("https://"):
        raise ValueError("URL must use the https scheme")
    return url


HttpsUrl = Annotated[str, Field(min_length=9), AfterValidator(_require_https)]


# ---------------------------------------------------------------------------
# Example model using all constrained types
# ---------------------------------------------------------------------------

class Product(BaseModel):
    """A product listing — demonstrates every constrained type in one model."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    id: PositiveInt
    name: NonEmptyStr
    contact_email: Email
    price: MoneyAmount
    discount_pct: Percentage
    info_url: HttpsUrl


# ---------------------------------------------------------------------------
# Usage demonstration
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    product = Product(
        id=42,
        name="Ergonomic Keyboard",
        contact_email="sales@example.com",
        price=Decimal("149.99"),
        discount_pct=Decimal("12.5"),
        info_url="https://example.com/products/ergonomic-keyboard",
    )
    print(product.model_dump())

    # Validation errors are raised immediately on construction — no silent coercion.
    import pydantic

    bad_cases = [
        # id must be > 0
        dict(id=0, name="X", contact_email="a@b.com", price=Decimal("1.00"), discount_pct=Decimal("0"), info_url="https://x.com"),
        # name must be non-empty
        dict(id=1, name="", contact_email="a@b.com", price=Decimal("1.00"), discount_pct=Decimal("0"), info_url="https://x.com"),
        # email must match pattern
        dict(id=1, name="X", contact_email="not-an-email", price=Decimal("1.00"), discount_pct=Decimal("0"), info_url="https://x.com"),
        # price must be positive
        dict(id=1, name="X", contact_email="a@b.com", price=Decimal("-5.00"), discount_pct=Decimal("0"), info_url="https://x.com"),
        # percentage must be 0–100
        dict(id=1, name="X", contact_email="a@b.com", price=Decimal("1.00"), discount_pct=Decimal("101"), info_url="https://x.com"),
        # URL must be https
        dict(id=1, name="X", contact_email="a@b.com", price=Decimal("1.00"), discount_pct=Decimal("0"), info_url="http://insecure.com"),
    ]

    for case in bad_cases:
        try:
            Product(**case)
        except pydantic.ValidationError as exc:
            print(exc.errors()[0]["msg"])
