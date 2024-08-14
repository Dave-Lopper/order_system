from typing import Any, Generator

import pytest
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, clear_mappers, Session

from order_system.orm import metadata, start_mappers


@pytest.fixture
def in_memory_db() -> Engine:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db: Engine) -> Generator[Session, Any, None]:
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()
