import time
import redis
from nameko.rpc import rpc, RpcProxy
from cabinet import Cabinet, CachedCabinet, RedisEngine
from app import REDIS_POOL
import settings


class SubscriberProcessorService:
    name = "subscriber_processor_service"

    counter_service = RpcProxy("counter_service")
    queue = RpcProxy("queue")

    @rpc
    def process_subscriber(self, payload):
        print("SubscriberProcessorService.process_subscriber: "
              f"processing subscriber: {payload['subscriber']}")
        start_time = time.time()
        redis_client = redis.Redis(connection_pool=REDIS_POOL)
        cab = Cabinet(settings.CABINET_URL)
        cached_cabinet = CachedCabinet(
            cab,
            RedisEngine(redis_client, prefix="CABINET_CACHE", ttl=30))
        general_settings = cached_cabinet.general()
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        print("SubscriberProcessorService.process_subscriber: "
              f"received settings in {int(total_time)}ms")
        limit = general_settings["push_limit_per_token"]
        start_time2 = time.time()
        subscriber_pushes = (self.counter_service
                             .get_pushes_count(payload["subscriber"]["_id"]))
        end_time2 = time.time()
        print("SubscriberProcessorService.process_subscriber: "
              f"get_pushes_count in {(end_time2 - start_time2) * 1000}ms")
        if subscriber_pushes < limit:
            self.queue.publish.call_async(payload)
        else:
            print("SubscriberProcessorService.process_subscriber: "
                  f"limit for subscriber: {payload} exceeded")
        finish_time = time.time()
        print("SubscriberProcessorService.process_subscriber: "
              f"total execution time {(finish_time - start_time) * 1000}ms")
