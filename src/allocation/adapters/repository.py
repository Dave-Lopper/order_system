from typing import Protocol

from sqlalchemy.exc import NoResultFound  # type: ignore
from sqlalchemy.orm import Session  #  type: ignore

from src.allocation.adapters import orm
from src.allocation.domain import model


class AbstractRepository(Protocol):
    seen: set[model.Product] = set()

    def __init__(self) -> None:
        self.seen: set[model.Product] = set()

    def add(self, product: model.Product):
        self._add(product)
        self.seen.add(product)

    def _add(self, product: model.Product):
        ...

    def get(self, sku: str) -> model.Product | None:
        product = self._get(sku)
        if product:
            self.seen.add(product)
        return product

    def get_by_batchref(self, reference: str) -> model.Product | None:
        product = self._get_by_batchref(reference)
        if product:
            self.seen.add(product)
        return product

    def _get_by_batchref(self, reference: str) -> model.Product | None:
        ...

    def _get(self, rederence: str) -> model.Product | None:
        ...

    def list(self) -> list[model.Product]:
        ...


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session):
        super().__init__()
        self.session = session

    def _add(self, product: model.Product):
        self.session.add(product)

    def _get(self, sku: str) -> model.Product | None:
        try:
            return self.session.query(model.Product).filter_by(sku=sku).one()
        except NoResultFound:
            return None

    def _get_by_batchref(self, reference: str) -> model.Product | None:
        return (
            self.session.query(model.Product)
            .join(model.Batch)
            .filter(orm.batches.c.reference == reference)
            .first()
        )

    def list(self) -> list[model.Product]:
        return self.session.query(model.Product).all()


class FakeRepository(AbstractRepository):
    def __init__(self, products: list[model.Product]):
        super().__init__()
        self._products = set(products)

    def _add(self, product: model.Product):
        self._products.add(product)

    def _get(self, sku: str) -> model.Product | None:
        return next(b for b in self._products if b.sku == sku)

    def _get_by_batchref(self, reference: str) -> model.Product | None:
        return next(
            (
                p
                for p in self._products
                for b in p.batches
                if b.reference == reference
            )
        )

    def list(self) -> list[model.Product]:
        return list(self._products)
