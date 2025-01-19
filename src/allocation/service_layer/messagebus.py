from __future__ import annotations
from typing import Callable, Type, TYPE_CHECKING

from tenacity import Retrying, RetryError, stop_after_attempt, wait_exponential

from src.allocation.domain import events, commands
from . import handlers

if TYPE_CHECKING:
    from . import unit_of_work




Message = events.Event | commands.Command


EVENT_HANDLERS: dict[Type[events.Event], list[Callable]] = {
    events.OutOfStock: [handlers.send_out_of_stock_notification],
    events.Allocated: [handlers.publish_allocated_event],
}
COMMAND_HANDLERS: dict[Type[commands.Command], Callable] = {
    commands.Allocate: handlers.allocate,
    commands.CreateBatch: handlers.add_batch,
    commands.ChangeBatchQuantity: handlers.change_batch_quantity,
}


def handle_command(
    command: commands.Command,
    queue: list[Message],
    uow: unit_of_work.AbstractUnitOfWork,
):
    print(f"handling command {command}")
    try:
        handler = COMMAND_HANDLERS[type(command)]  #(1)
        result = handler(command, uow=uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        print(f"Exception handling command {command}")
        raise




def handle_event(
    event: events.Event,
    queue: list[Message],
    uow: unit_of_work.AbstractUnitOfWork,
):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            for attempt in Retrying(
                stop=stop_after_attempt(3),
                wait=wait_exponential()
            ):

                with attempt:
                    print(f"handling event {event} with handler {handler}")
                    handler(event, uow=uow)
                    queue.extend(uow.collect_new_events())
        except RetryError as retry_failure:
            print(
                f"Failed to handle event {retry_failure.last_attempt.attempt_number} times, giving up!"
            )
            continue


def handle(
    message: Message,
    uow: unit_of_work.AbstractUnitOfWork,
):
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            cmd_result = handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
            raise Exception(f"{message} was not an Event or Command")
    return results

