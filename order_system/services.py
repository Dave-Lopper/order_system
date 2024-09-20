from datetime import date
from typing import Optional

from order_system import domain, unit_of_work


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[domain.Batch]):
    return sku in {b.sku for b in batches}


def add_batch(
    ref: str,
    sku: str,
    quantity: int,
    eta: Optional[date],
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    with uow:
        uow.batches.add(
            domain.Batch(ref=ref, sku=sku, quantity=quantity, eta=eta)
        )
        uow.commit()


def allocate(
    order_id: str,
    sku: str,
    quantity: int,
    uow: unit_of_work.AbstractUnitOfWork,
) -> str:
    line = domain.OrderLine(order_ref=order_id, sku=sku, quantity=quantity)
    with uow:
        batches = uow.batches.list()
        if not is_valid_sku(sku, batches):
            raise InvalidSku(f"Invalid sku {sku}")
        batchref = domain.allocate(line, batches)
        uow.commit()
    return batchref


def reallocate(
    line: domain.OrderLine,
    uow: unit_of_work.AbstractUnitOfWork,
) -> str:
    with uow:
        batch = uow.batches.get(reference=line.sku)
        if batch is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        batch.deallocate(line)
        batchref = allocate(line.order_ref, line.sku, line.quantity, uow)
        uow.commit()
    return batchref
