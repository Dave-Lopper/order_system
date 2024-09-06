from datetime import date, timedelta

import pytest

from order_system.domain import Batch, OrderLine, allocate, OutOfStock


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch(
        ref="batch-001",
        sku="SMALL-TABLE",
        quantity=20,
        eta=date.today(),
    )
    line = OrderLine(order_ref="order-ref", sku="SMALL-TABLE", quantity=2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def make_batch_and_line(sku: str, batch_quantity: int, line_quantity: int):
    return (
        Batch(
            ref="batch-001",
            sku=sku,
            quantity=batch_quantity,
            eta=date.today(),
        ),
        OrderLine(order_ref="order-123", sku=sku, quantity=line_quantity),
    )


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)
    assert small_batch.can_allocate(large_line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch(
        ref="batch-001",
        sku="UNCOMFORTABLE-CHAIR",
        quantity=100,
        eta=None,
    )
    different_sku_line = OrderLine(
        order_ref="order-123", sku="EXPENSIVE-TOASTER", quantity=10
    )
    assert batch.can_allocate(different_sku_line) is False


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18


def test_prefers_current_stock_batches_to_shipments():
    tomorrow = date.today() + timedelta(days=1)
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)
    line = OrderLine(order_ref="oref", sku="RETRO-CLOCK", quantity=10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    today = date.today()
    tomorrow = today + timedelta(days=1)
    later = tomorrow + timedelta(days=1)

    earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=today)
    medium = Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=tomorrow)
    latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=later)
    line = OrderLine(order_ref="order1", sku="MINIMALIST-SPOON", quantity=10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    today = date.today()
    tomorrow = today + timedelta(days=1)

    in_stock_batch = Batch(
        "in-stock-batch-ref",
        "HIGHBROW-POSTER",
        100,
        eta=None,
    )
    shipment_batch = Batch(
        "shipment-batch-ref",
        "HIGHBROW-POSTER",
        100,
        eta=tomorrow,
    )
    line = OrderLine(order_ref="oref", sku="HIGHBROW-POSTER", quantity=10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    today = date.today()
    batch = Batch("batch1", "SMALL-FORK", 10, eta=today)
    allocate(
        OrderLine(order_ref="order1", sku="SMALL-FORK", quantity=10), [batch]
    )

    with pytest.raises(OutOfStock, match="SMALL-FORK"):
        allocate(
            OrderLine(order_ref="order2", sku="SMALL-FORK", quantity=1),
            [batch],
        )
