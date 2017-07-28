import redis
import pika
import pika_pool
from elasticsearch import Elasticsearch

import settings


REDIS_POOL = redis.ConnectionPool.from_url(settings.REDIS_URI)

es = Elasticsearch([settings.ELASTIC_URI])

# 'amqp://guest:guest@localhost:5672/
pika_params = pika.URLParameters(
    settings.EXT_AMQP_URI + '?'
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


# country_whitelist = []
country_blacklist = ["VNM", "IND", "IDN", "PHL", "ROU", "COL", "THA", "MEX",
                     "MYS", "MAR", "HUN", "ESP", "ITA", "PAK", "TUR", "TWN",
                     "CHL", "GEO", "PER", "CZE", "AZE", "SRB", "KAZ"]

country_whitelist = ["AZE"]

hours_whitelist = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

campaigns = [
    {
        "id": 1,
        "dsp_id": 1,
        "total_limit": 100000,
        "daily_limit": 1000,
        "targetings": [
            {
                "field": "country",
                "operator": "NOT IN",
                "value": country_blacklist
            }
        ]
    }
]
