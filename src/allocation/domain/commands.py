from datetime import date
from dataclasses import dataclass

class Command:
    pass


@dataclass
class Allocate(Command):  #(1)
    orderid: str
    sku: str
    qty: int


@dataclass
class CreateBatch(Command):  #(2)
    ref: str
    sku: str
    qty: int
    eta: date | None = None


@dataclass
class ChangeBatchQuantity(Command):  #(3)
    ref: str
    qty: int