from __future__ import annotations

from pydantic import BaseModel, computed_field, field_serializer, model_config


class Product(BaseModel):
    model_config = model_config(frozen=True)

    name: str
    price_cents: int
    tax_rate: float
    quantity: int

    @computed_field
    @property
    def price_dollars(self) -> float:
        return self.price_cents / 100

    @computed_field
    @property
    def tax_amount(self) -> float:
        return round(self.price_dollars * self.tax_rate * self.quantity, 2)

    @computed_field
    @property
    def total(self) -> float:
        return round(self.price_dollars * self.quantity + self.tax_amount, 2)

    @field_serializer("price_dollars")
    def serialize_price_dollars(self, value: float) -> str:
        return f"${value:,.2f}"

    @field_serializer("tax_amount")
    def serialize_tax_amount(self, value: float) -> str:
        return f"${value:,.2f}"

    @field_serializer("total")
    def serialize_total(self, value: float) -> str:
        return f"${value:,.2f}"


if __name__ == "__main__":
    product = Product(
        name="Widget",
        price_cents=1999,
        tax_rate=0.08,
        quantity=3,
    )

    print(product.model_dump_json(indent=2))
