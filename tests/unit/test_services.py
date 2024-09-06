import pytest

from order_system import repository, services


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_add_batch():
    repo, session = repository.FakeRepository([]), FakeSession()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.committed


def test_returns_allocation():
    repo, session = repository.FakeRepository([]), FakeSession()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, repo, session)

    result = services.allocate(
        order_id="o1",
        sku="COMPLICATED-LAMP",
        quantity=10,
        repo=repo,
        session=session,
    )
    assert result == "batch1"


def test_error_for_invalid_sku():
    repo, session = repository.FakeRepository([]), FakeSession()
    services.add_batch("b1", "AREALSKU", 100, None, repo, session)

    with pytest.raises(
        services.InvalidSku,
        match="Invalid sku NONEXISTENTSKU",
    ):
        services.allocate(
            order_id="o1",
            sku="NONEXISTENTSKU",
            quantity=100,
            repo=repo,
            session=FakeSession(),
        )


def test_commits():
    repo, session = repository.FakeRepository([]), FakeSession()
    services.add_batch("b1", "AREALSKU", 100, None, repo, session)
    session = FakeSession()

    services.allocate(
        order_id="o1", sku="AREALSKU", quantity=10, repo=repo, session=session
    )
    assert session.committed is True
