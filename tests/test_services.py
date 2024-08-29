import pytest

from order_system import domain, repository, services


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    line = domain.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = domain.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = repository.FakeRepository([batch])  # (1)

    result = services.allocate(line, repo, FakeSession())  # (2) (3)
    assert result == "b1"


def test_error_for_invalid_sku():
    line = domain.OrderLine(order_ref="o1", sku="NONEXISTENTSKU", quantity=10)
    batch = domain.Batch(ref="b1", sku="AREALSKU", quantity=100, eta=None)
    repo = repository.FakeRepository([batch])  # (1)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())  # (2) (3)


def test_commits():
    line = domain.OrderLine(order_ref="o1", sku="OMINOUS-MIRROR", quantity=10)
    batch = domain.Batch(ref="b1", sku="OMINOUS-MIRROR", quantity=100, eta=None)
    repo = repository.FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True
