import redis
from nameko.rpc import rpc
from app import REDIS_POOL


class CounterService:
    name = "counter_service"

    @rpc
    def get_pushes_count(self, token):
        client = redis.Redis(connection_pool=REDIS_POOL,
                             socket_timeout=1)
        value = client.get(f"subscriber.pushes.count:{token}")
        try:
            return int(value)
        except TypeError:
            # If None returned
            return 0
