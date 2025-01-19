from loguru import logger
import redis

from src.allocation import config
from src.allocation.domain import events

r = redis.Redis(**config.get_redis_host_and_port())

def publish(channel: str, event: events.Event) -> None:
    logger.info(f"publishing: {event} to {channel}")
    r.publish(channel, event.json())