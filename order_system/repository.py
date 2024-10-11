from typing import Protocol

from order_system import domain
from sqlalchemy.orm import Session


class AbstractRepository(Protocol):
    def add(self, product: domain.Product): ...

    def get(self, reference: str) -> domain.Product: ...
    
    def list(self) -> list[domain.Product]: ...


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session: Session):
        self.session = session

    def add(self, product: domain.Product):
        self.session.add(product)

    def get(self, sku: str) -> domain.Product:
        return (
            self.session.query(domain.Product)
            .filter_by(sku=sku)
            .one()
        )

    def list(self) -> list[domain.Product]:
        return self.session.query(domain.Product).all()


class FakeRepository(AbstractRepository):

    def __init__(self, productes: list[domain.Product]):
        self._productes = set(productes)

    def add(self, product: domain.Product):
        self._productes.add(product)

    def get(self, reference: str) -> domain.Product:
        return next(b for b in self._productes if b.reference == reference)

    def list(self) -> list[domain.Product]:
        return list(self._productes)
