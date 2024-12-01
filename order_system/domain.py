from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Set

from pydantic import BaseModel


@dataclass(unsafe_hash=True)
class OrderLine:
    order_ref: str
    sku: str
    quantity: int


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


class Event:
    pass

@dataclass
class OutOfStock(Event):
    sku: str


class Product:
    events: list[Event] = []

    def __init__(
        self, sku: str,
        batches: List[Batch],
        version_number: int = 0
    ):
        self.sku = sku
        self.batches = batches
        self.version_number = version_number
        self.events = []

    def allocate(self, line: OrderLine) -> str | None:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
            self.version_number += 1
            return batch.reference
        except StopIteration:
            self.events.append(OutOfStock(line.sku))
            return None

