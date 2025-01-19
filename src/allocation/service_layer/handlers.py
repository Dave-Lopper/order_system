from dataclasses import asdict

from sqlalchemy.sql import text

from src.allocation.adapters import email, redis_eventpublisher
from src.allocation.domain import commands, events, model
from src.allocation.service_layer import unit_of_work


class InvalidSku(Exception):
    pass

def add_batch(
    event: events.BatchCreated,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        product = uow.products.get(sku=event.sku)
        if product is None:
            product = model.Product(event.sku, batches=[])
            uow.products.add(product)
        product.batches.append(
            model.Batch(event.ref, event.sku, event.qty, event.eta)
        )
        uow.commit()


def allocate(
    event: events.AllocationRequired,
    uow: unit_of_work.AbstractUnitOfWork,
) -> str | None:
    line = model.OrderLine(event.orderid, event.sku, event.qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        batchref = product.allocate(line)
        uow.commit()
        return batchref


def change_batch_quantity(event: events.BatchQuantityChanged, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        product = uow.products.get_by_batchref(reference=event.ref)
        product.change_batch_quantity(ref=event.ref, qty=event.qty)
        uow.commit()


def send_out_of_stock_notification(
    event: events.OutOfStock,
    uow: unit_of_work.AbstractUnitOfWork,
):
    email.send(
        "stock@made.com",
        f"Out of stock for {event.sku}",
    )


def publish_allocated_event(
    event: events.Allocated,
    uow: unit_of_work.AbstractUnitOfWork,
):
    redis_eventpublisher.publish("line_allocated", event)

def add_allocation_to_read_model(
    event: events.Allocated,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        uow.session.execute(
            text("""
            INSERT INTO allocations_view (orderid, sku, batchref)
            VALUES (:orderid, :sku, :batchref)
            """),
            
        )
        uow.commit()

def remove_allocation_from_read_model(
    event: events.Deallocated,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            text("""
            DELETE FROM allocations_view
            WHERE orderid = :orderid AND sku = :sku
            """),
            dict(orderid=event.orderid, sku=event.sku),
        )
        uow.commit()

def reallocate(
    event: events.Deallocated,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        product = uow.products.get(sku=event.sku)
        product.events.append(commands.Allocate(**asdict(event)))
        uow.commit()