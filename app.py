import sys
import logging
import redis
import pika
import pika_pool

from elasticsearch_dsl.connections import connections
import settings


REDIS_POOL = redis.ConnectionPool.from_url(settings.REDIS_URI)

es = connections.create_connection(hosts=[settings.ELASTIC_URI])

# 'amqp://guest:guest@localhost:5672/
pika_params = pika.URLParameters(
    settings.AMQP_URI + '?'
    'socket_timeout=10&'
    'connection_attempts=2'
)

rmq_pool = pika_pool.QueuedPool(
    create=lambda: pika.BlockingConnection(parameters=pika_params),
    max_size=10,
    max_overflow=10,
    timeout=10,
    recycle=3600,
    stale=45,
)

hours_whitelist = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]


logger = logging.getLogger()
logger.setLevel(getattr(logging, settings.LOG_LEVEL))
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(getattr(logging, settings.LOG_LEVEL))
logger.addHandler(ch)
