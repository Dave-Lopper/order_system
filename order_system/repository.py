from typing import Protocol

from order_system import domain
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session


class AbstractRepository(Protocol):
    seen: set[domain.Product] = set()

    def __init__(self) -> None:
       self.seen: set[domain.Product] = set()
 
    def add(self, product: domain.Product):
        self._add(product)
        self.seen.add(product)

    def _add(self, product: domain.Product): ...

    def get(self, reference: str) -> domain.Product | None:
        product = self._get(reference)
        if product:
            self.seen.add(product)
        return product
    
    def _get(self, rederence: str) -> domain.Product | None: ...
    
    def list(self) -> list[domain.Product]: ...


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session: Session):
        super().__init__()
        self.session = session

    def _add(self, product: domain.Product):
        self.session.add(product)

    def _get(self, sku: str) -> domain.Product | None:
        try:
            return (
                self.session.query(domain.Product)
                .filter_by(sku=sku)
                .one()
            )
        except NoResultFound:
            return None

    def list(self) -> list[domain.Product]:
        return self.session.query(domain.Product).all()


class FakeRepository(AbstractRepository):

    def __init__(self, products: list[domain.Product]):
        super().__init__()
        self._products = set(products)

    def _add(self, product: domain.Product):
        self._products.add(product)

    def _get(self, reference: str) -> domain.Product | None:
        return next(b for b in self._products if b.sku == reference)

    def list(self) -> list[domain.Product]:
        return list(self._products)
