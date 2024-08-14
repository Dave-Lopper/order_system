from typing import Protocol

from order_system import domain


class AbstractRepository(Protocol):
    def add(self, batch: domain.Batch): ...

    def get(self, reference: str) -> domain.Batch: ...


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch: domain.Batch):
        self.session.add(batch)

    def get(self, reference: str) -> domain.Batch:
        return (
            self.session.query(domain.Batch)
            .filter_by(reference=reference)
            .one()
        )

    def list(self) -> list[domain.Batch]:
        return self.session.query(domain.Batch).all()


class FakeRepository(AbstractRepository):

    def __init__(self, batches: list[domain.Batch]):
        self._batches = set(batches)

    def add(self, batch: domain.Batch):
        self._batches.add(batch)

    def get(self, reference: str) -> domain.Batch:
        return next(b for b in self._batches if b.reference == reference)

    def list(self) -> list[domain.Batch]:
        return list(self._batches)
