from datetime import date

from order_system.domain import Batch, Product, OrderLine, OutOfStock


today = date.today()

def test_records_out_of_stock_event_if_cannot_allocate():
    batch = Batch("batch1", "SMALL-FORK", 10, eta=today)
    product = Product(sku="SMALL-FORK", batches=[batch])
    product.allocate(OrderLine("order1", "SMALL-FORK", 10))

    allocation = product.allocate(OrderLine("order2", "SMALL-FORK", 1))
    assert product.events[-1] == OutOfStock(sku="SMALL-FORK")  #(1)
    assert allocation is None