from abc import ABC, abstractmethod
from typing import Any
from pickle import dumps, loads
from dataclasses import dataclass

from redis import Redis
from eric_sse import get_logger
from eric_sse.exception import NoMessagesException, RepositoryError
from eric_sse.message import MessageContract
from eric_sse.queues import Queue
from eric_sse import generate_uuid

logger = get_logger()

PREFIX = 'eric-redis-queues'
PREFIX_QUEUES = f'{PREFIX}:q'
PREFIX_LISTENERS = f'{PREFIX}:l'
PREFIX_CONNECTIONS = f'{PREFIX}:c'
PREFIX_CHANNELS = f'{PREFIX}:chn'
PREFIX_MESSAGES = f'{PREFIX}:m'

CONNECTION_REPOSITORY_DEFAULT = 'eric_redis_queues.RedisConnectionsRepository'
CONNECTION_REPOSITORY_BLOCKING = 'eric_redis_queues.RedisBlockingQueuesRepository'

QUEUE_TYPE_DEFAULT = 'default'
QUEUE_TYPE_BLOCKING = 'blocking'

@dataclass
class RedisConnection:
    host: str = '127.0.0.1'
    port: int = 6379
    db: int = 0

class AbstractRedisQueue(Queue, ABC):

    def __init__(self, redis_connection: RedisConnection, queue_id: str = None):
        super().__init__()
        self.queue_id = queue_id if queue_id else generate_uuid()
        self.redis_connection = redis_connection
        self._client = Redis(host=redis_connection.host, port=redis_connection.port, db=redis_connection.db)

    def to_dict(self) -> dict:
        return {
            'queue_id': self.queue_id,
            'redis_connection': self.redis_connection
        }



class RedisQueue(AbstractRedisQueue):

    def pop(self) -> Any | None:
        try:
            raw_value = self._client.lpop(f'{PREFIX_MESSAGES}:{self.queue_id}')
            if raw_value is None:
                raise NoMessagesException
            return loads(bytes(raw_value))

        except NoMessagesException:
            raise
        except Exception as e:
            raise RepositoryError(e)

    def push(self, msg: MessageContract) -> None:
        try:
            self._client.rpush(f'{PREFIX_MESSAGES}:{self.queue_id}', dumps(msg))
        except Exception as e:
            raise RepositoryError(e)

    def to_dict(self) -> dict:
        result = super().to_dict()
        result['type'] = QUEUE_TYPE_DEFAULT
        return result

class BlockingRedisQueue(AbstractRedisQueue):
    """Implements a blocking queue. See **pop()** documentation"""

    def pop(self) -> Any | None:
        """Behaviour relies on https://redis.io/docs/latest/commands/blpop/ , so calls to it with block program execution until a new message is pushed."""

        k, v = self._client.blpop([f'{PREFIX_MESSAGES}:{self.queue_id}'])
        return loads(bytes(v))

    def push(self, msg: MessageContract) -> None:
        try:
            self._client.rpush(f'{PREFIX_MESSAGES}:{self.queue_id}', dumps(msg))
        except Exception as e:
            raise RepositoryError(e)

    def to_dict(self) -> dict:
        result = super().to_dict()
        result['type'] = QUEUE_TYPE_BLOCKING
        return result