import email
from typing import Callable, Type

from order_system.domain import Event, OutOfStock



def send_out_of_stock_notification(event: OutOfStock):
    print(
        "stock@made.com",
        f"Out of stock for {event.sku}",
    )


HANDLERS: dict[Type[Event], list[Callable]] = {
    OutOfStock: [send_out_of_stock_notification]
}


def handle(event: Event):
    for handler in HANDLERS[type(event)]:
        handler(event)