from datetime import date

from typing import List, Optional, Set

from pydantic import BaseModel


class OrderLine(BaseModel):
    order_ref: str
    sku: str
    quantity: int

    class Config:
        frozen = True


class Order(BaseModel):
    ref: str
    lines: List[OrderLine]


class Batch:
    def __init__(self, ref: str, sku: str, quantity: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = quantity
        self._allocations: Set[OrderLine] = set()

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.quantity for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return (
            self.sku == line.sku and self.available_quantity >= line.quantity
        )  # noqe: E501


class Product(BaseModel):
    sku: str
    display_name: Optional[str] = None


class OutOfStock(Exception):
    pass


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
    batch.allocate(line)
    return batch.reference
