import pytest

from order_system import services, unit_of_work


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_error_for_invalid_sku():
    uow = unit_of_work.FakeUnitOfWork()
    services.add_batch("b1", "AREALSKU", 100, None, uow)

    with pytest.raises(
        services.InvalidSku,
        match="Invalid sku NONEXISTENTSKU",
    ):
        services.allocate(
            order_id="o1",
            sku="NONEXISTENTSKU",
            quantity=100,
            uow=uow
        )


def test_commits():
    uow = unit_of_work.FakeUnitOfWork()
    services.add_batch("b1", "AREALSKU", 100, None, uow)

    services.allocate(
        order_id="o1", sku="AREALSKU", quantity=10, uow=uow 
    )
    assert uow.committed is True


def test_add_batch():
    uow = unit_of_work.FakeUnitOfWork()  # (3)
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)  # (3)
    assert uow.batches.get("b1") is not None
    assert uow.committed


def test_allocate_returns_allocation():
    uow = unit_of_work.FakeUnitOfWork()  # (3)
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)  # (3)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)  # (3)
    assert result == "batch1"
