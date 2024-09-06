from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from order_system import domain, repository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[domain.Batch]):
    return sku in {b.sku for b in batches}


def add_batch(
    ref: str,
    sku: str,
    quantity: int,
    eta: Optional[date],
    repo: repository.AbstractRepository,
    session: Session,
) -> None:
    repo.add(domain.Batch(ref=ref, sku=sku, quantity=quantity, eta=eta))
    session.commit()


def allocate(
    order_id: str,
    sku: str,
    quantity: int,
    repo: repository.AbstractRepository,
    session: Session,
) -> str:
    batches = repo.list()
    if not is_valid_sku(sku, batches):
        raise InvalidSku(f"Invalid sku {sku}")
    line = domain.OrderLine(order_ref=order_id, sku=sku, quantity=quantity)
    batchref = domain.allocate(line, batches)
    session.commit()
    return batchref
