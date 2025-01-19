from dataclasses import dataclass
from datetime import date


class Event:
    pass


@dataclass
class Allocated(Event):
    orderid: str
    sku: str
    qty: int
    batchref: str


@dataclass
class BatchCreated(Event):
    ref: str
    sku: str
    qty: int
    eta: date | None = None


@dataclass
class BatchQuantityChanged(Event):
    ref: str
    qty: int


@dataclass
class AllocationRequired(Event):
    orderid: str
    sku: str
    qty: int


@dataclass
class OutOfStock(Event):
    sku: str