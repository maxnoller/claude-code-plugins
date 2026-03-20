"""Reusable constrained types for cross-codebase use with Pydantic v2."""

from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, HttpUrl


# --- Constrained type definitions ---

PositiveInt = Annotated[int, Field(gt=0)]

NonEmptyStr = Annotated[str, Field(min_length=1)]

Email = Annotated[
    str,
    Field(pattern=r"^[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}$"),
]

# Positive decimal with exactly 2 decimal places.
# Uses Decimal for precision — no floating-point rounding errors.
MoneyAmount = Annotated[
    Decimal,
    Field(gt=0, decimal_places=2),
]

# 0–100 inclusive, supports fractional percentages (e.g. 99.9).
Percentage = Annotated[float, Field(ge=0.0, le=100.0)]


def _require_https(url: HttpUrl) -> HttpUrl:
    if url.scheme != "https":
        raise ValueError(f"URL must use https, got: {url.scheme}")
    return url


# HttpUrl already validates URL structure; the AfterValidator enforces https.
HttpsUrl = Annotated[HttpUrl, AfterValidator(_require_https)]


# --- Example model using the constrained types ---

class ProductListing(BaseModel):
    """An e-commerce product listing demonstrating all constrained types."""

    model_config = ConfigDict(strict=True, frozen=True)

    id: PositiveInt
    name: NonEmptyStr
    seller_email: Email
    price: MoneyAmount
    discount_pct: Percentage
    product_url: HttpsUrl


# --- Usage ---

if __name__ == "__main__":
    listing = ProductListing(
        id=42,
        name="Ergonomic Keyboard",
        seller_email="seller@example.com",
        price=Decimal("149.99"),
        discount_pct=12.5,
        product_url="https://shop.example.com/keyboards/ergonomic",  # type: ignore[arg-type]
    )
    print(listing.model_dump())
