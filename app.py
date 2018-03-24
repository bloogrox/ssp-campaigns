import sys
import logging
import redis
import pika
import pika_pool

from elasticsearch_dsl.connections import connections
import settings


REDIS_POOL = redis.ConnectionPool.from_url(settings.REDIS_URI)

es = connections.create_connection(hosts=[settings.ELASTIC_URI])

pika_params = pika.URLParameters(
    settings.AMQP_URI + '?'
    'socket_timeout=1&'
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

logger = logging.getLogger('Campaigns')
logger.setLevel(getattr(logging, settings.LOG_LEVEL))
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(getattr(logging, settings.LOG_LEVEL))
logger.addHandler(ch)


from actors.queue import Queue  # noqa

queue_ref = Queue.start()

from actors.subscriber_processor import SubscriberProcessor  # noqa

subscriber_processor_ref = SubscriberProcessor.start()

# from actors.ssp import SSP  # noqa

# ssp_ref = SSP.start()
