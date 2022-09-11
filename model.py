from uuid import uuid4
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


def random_unique_reference() -> str:
    return str(uuid4())


@dataclass
class Batch:
    batch_reference: str
    sku: str
    available_quantity: int
    eta: datetime | None

    @property
    def is_warehouse_stock(self) -> bool:
        return self.eta is None


@dataclass
class OrderLine:
    sku: str
    quantity: int


@dataclass
class Order:
    order_reference: str
    order_lines: list[OrderLine]

    @classmethod
    def allocate_order_lines(
        cls, *, order_lines: list[OrderLine], batches: list[Batch]
    ) -> "Order":
        return Order(
            order_reference=random_unique_reference(),
            order_lines=[],
        )
