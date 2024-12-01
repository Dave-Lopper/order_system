import pytest

from order_system import domain, services, unit_of_work


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_error_for_invalid_sku():
    uow = unit_of_work.FakeUnitOfWork([
        domain.Product(
            sku="AREALSKU",
            batches=[domain.Batch(
                ref=f"ref_{i}", sku="AREALSKU", quantity=10*i, eta=None
            ) for i in range(5)],
            version_number=5)
    ])
    services.add_batch("b1", "AREALSKU", 100, None, uow)

    with pytest.raises(StopIteration):
        services.allocate(
            order_id="o1",
            sku="NONEXISTENTSKU",
            quantity=100,
            uow=uow
        )


def test_commits():
    uow = unit_of_work.FakeUnitOfWork([
        domain.Product(
            sku="AREALSKU",
            batches=[domain.Batch(
                ref=f"ref_{i}", sku="AREALSKU", quantity=10*i, eta=None
            ) for i in range(5)],
            version_number=5)
    ])
    services.add_batch("b1", "AREALSKU", 100, None, uow)

    services.allocate(
        order_id="o1", sku="AREALSKU", quantity=10, uow=uow 
    )
    assert uow.committed is True


def test_add_batch():
    uow = unit_of_work.FakeUnitOfWork([
        domain.Product(
            sku="CRUNCHY-ARMCHAIR",
            batches=[],
            version_number=5)
    ])
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)  # (3)
    product = uow.products.get("CRUNCHY-ARMCHAIR")
    assert product is not None
    assert product.batches
    batch = product.batches[0]
    assert batch.reference == "b1"
    assert batch.sku == "CRUNCHY-ARMCHAIR"
    assert batch.eta is None
    assert uow.committed


def test_allocate_returns_allocation():
    uow = unit_of_work.FakeUnitOfWork([
        domain.Product(
            sku="COMPLICATED-LAMP",
            batches=[],
            version_number=5
        )
    ])
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)  # (3)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)  # (3)
    assert result == "batch1"
