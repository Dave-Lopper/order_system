from sqlalchemy.orm import Session

from order_system import domain, repository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[domain.Batch]):
    return sku in {b.sku for b in batches}


def allocate(
    line: domain.OrderLine,
    repo: repository.AbstractRepository,
    session: Session,
) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = domain.allocate(line, batches)
    session.commit()
    return batchref
