from functools import cached_property
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer

PositiveInt = Annotated[int, Field(gt=0)]
NonEmptyStr = Annotated[str, Field(min_length=1)]
PositiveFloat = Annotated[float, Field(gt=0)]


class Product(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    name: NonEmptyStr
    price_cents: PositiveInt
    tax_rate: PositiveFloat
    quantity: PositiveInt

    @computed_field
    @cached_property
    def price_dollars(self) -> float:
        return self.price_cents / 100

    @computed_field
    @cached_property
    def tax_amount(self) -> float:
        return self.price_dollars * self.tax_rate

    @computed_field
    @cached_property
    def total(self) -> float:
        return (self.price_dollars + self.tax_amount) * self.quantity

    @field_serializer("price_dollars", "tax_amount", "total")
    def serialize_as_dollars(self, v: float, _info) -> str:
        return f"${v:.2f}"
