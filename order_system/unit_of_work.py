from typing import Protocol

from order_system import config, repository

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class AbstractUnitOfWork(Protocol):
    products: repository.AbstractRepository

    def __exit__(self, *args):
        self.rollback()

    def __enter__(self): ...

    def commit(self): ...

    def rollback(self): ...


DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(config.get_db_uri(), isolation_level="REPEATABLE READ")
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.products = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        return super().rollback()


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.products = repository.FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
