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
        product = uow.products.get(sku=sku)
        if product is None:
            product = domain.Product(sku=sku, batches=[])
            uow.products.add(product)

        product.batches.append(
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
        product = uow.products.get(sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {sku}")
    
        batchref = product.allocate(line)
        uow.commit()
    return batchref


def reallocate(
    line: domain.OrderLine,
    uow: unit_of_work.AbstractUnitOfWork,
) -> str:
    with uow:
        product = uow.products.get(reference=line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        product.deallocate(line)
        batchref = product.allocate(line)
        uow.commit()
    return batchref
