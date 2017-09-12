import time
import redis
from nameko.rpc import rpc, RpcProxy
from cabinet import Cabinet, CachedCabinet, RedisEngine
from app import REDIS_POOL
import settings


DAY_SECONDS = 60 * 60 * 84


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
        bid_interval = general_settings["token_bid_interval"]
        start_time2 = time.time()
        token = payload["subscriber"]["_id"]
        subscriber_pushes = (self.counter_service
                             .get_pushes_count(token))
        end_time2 = time.time()
        print("SubscriberProcessorService.process_subscriber: "
              f"get_pushes_count in {(end_time2 - start_time2) * 1000}ms")
        has_quota = subscriber_pushes < limit
        last_push_key = f"subscriber:{token}:last-push-at"
        last_push_time = redis_client.get(last_push_key)
        if last_push_time:
            time_passed = time.time() - last_push_time
            time_passed_enough = time_passed > (bid_interval * 60)
            print("SubscriberProcessorService.process_subscriber: "
                  f"passed time since last push {time_passed}")
        else:
            time_passed_enough = True
        if has_quota and time_passed_enough:
            self.queue.publish.call_async(payload)
            redis_client.set(last_push_key, int(time.time()), ex=DAY_SECONDS)
        else:
            print("SubscriberProcessorService.process_subscriber: "
                  f"for subscriber: {payload} "
                  f"has_quota={has_quota} "
                  f"time_passed_enough={time_passed_enough}")
        finish_time = time.time()
        print("SubscriberProcessorService.process_subscriber: "
              f"total execution time {(finish_time - start_time) * 1000}ms")
