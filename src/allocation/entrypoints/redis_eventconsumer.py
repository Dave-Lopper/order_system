import json
from typing import Any

from loguru import logger
import redis

from src.allocation import bootstrap, config
from src.allocation.domain import commands
from src.allocation.service_layer import messagebus


r = redis.Redis(**config.get_redis_host_and_port())


def handle_change_batch_quantity(message: dict[str, Any], bus: messagebus.MessageBus) -> None:
    logger.info(f"{message=}")
    data = json.loads(message["data"])
    cmd = commands.ChangeBatchQuantity(ref=data["batchref"], qty=data["qty"])
    bus.handle(cmd)


def main():
    bus = bootstrap.bootstrap()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("change_batch_quantity")

    for message in pubsub.listen():
        handle_change_batch_quantity(message, bus)