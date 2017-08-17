import redis
from nameko.rpc import rpc, RpcProxy
from cabinet import Cabinet, CachedCabinet, RedisEngine
from app import REDIS_POOL


class SubscriberProcessorService:
    name = "subscriber_processor_service"

    counter_service = RpcProxy("counter_service")
    queue = RpcProxy("queue")

    @rpc
    def process_subscriber(self, payload):
        print("SubscriberProcessorService.process_subscriber: "
              f"processing subscriber: {payload['subscriber']}")
        redis_client = redis.Redis(connection_pool=REDIS_POOL)
        cab = Cabinet("https://ssp-cabinet.herokuapp.com")
        cached_cabinet = CachedCabinet(
            cab,
            RedisEngine(redis_client, prefix="CABINET_CACHE", ttl=5))
        general_settings = cached_cabinet.general()
        limit = general_settings["push_limit_per_token"]
        subscriber_pushes = (self.counter_service
                             .get_pushes_count(payload["subscriber"]["_id"]))
        if subscriber_pushes <= limit:
            self.queue.publish.call_async(payload)
        else:
            print("SubscriberProcessorService.process_subscriber: "
                  f"limit for subscriber: {payload} exceeded")
