from functools import cached_property
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer

# Reusable constrained types — define once, use everywhere
PositiveInt = Annotated[int, Field(gt=0)]
NonEmptyStr = Annotated[str, Field(min_length=1)]
NonNegativeFloat = Annotated[float, Field(ge=0.0)]
PositiveFloat = Annotated[float, Field(gt=0.0)]


def _format_dollars(cents: int) -> str:
    return f"${cents / 100:.2f}"


class Product(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    name: NonEmptyStr
    price_cents: PositiveInt
    tax_rate: NonNegativeFloat  # e.g. 0.08 for 8%
    quantity: PositiveInt

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def price_dollars(self) -> float:
        return self.price_cents / 100

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def tax_amount(self) -> float:
        return round(self.price_dollars * self.tax_rate, 2)

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def total(self) -> float:
        return round((self.price_dollars + self.tax_amount) * self.quantity, 2)

    @field_serializer("price_dollars")
    def serialize_price_dollars(self, value: float) -> str:  # noqa: ARG002
        return _format_dollars(self.price_cents)

    @field_serializer("tax_amount")
    def serialize_tax_amount(self, value: float) -> str:  # noqa: ARG002
        tax_cents = round(self.price_cents * self.tax_rate)
        return _format_dollars(tax_cents)

    @field_serializer("total")
    def serialize_total(self, value: float) -> str:  # noqa: ARG002
        tax_cents = round(self.price_cents * self.tax_rate)
        total_cents = (self.price_cents + tax_cents) * self.quantity
        return _format_dollars(total_cents)
