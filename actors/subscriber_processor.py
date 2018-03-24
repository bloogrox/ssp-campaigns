import time
import pykka
import redis
from cabinet import Cabinet, CachedCabinet, RedisEngine
from app import REDIS_POOL, logger, queue_ref, ssp_ref
import settings


DAY_SECONDS = 60 * 60 * 84


class SubscriberProcessor(pykka.ThreadingActor):
    def on_receive(self, payload):
        logger.debug("SubscriberProcessorService.process_subscriber: "
                     f"processing subscriber: {payload['subscriber']}")
        start_time = time.time()
        redis_client = redis.Redis(connection_pool=REDIS_POOL,
                                   socket_timeout=1)
        cab = Cabinet(settings.CABINET_URL)
        cached_cabinet = CachedCabinet(
            cab,
            RedisEngine(redis_client, prefix="CABINET_CACHE", ttl=30))
        general_settings = cached_cabinet.general()
        limit = general_settings["push_limit_per_token"]
        bid_interval = general_settings["token_bid_interval"]
        token = payload["subscriber"]["_id"]
        subscriber_pushes = redis_client.get(
            f"subscriber.pushes.count:{token}")
        try:
            subscriber_pushes = int(subscriber_pushes)
        except TypeError:
            subscriber_pushes = 0
        # subscriber_pushes = (self.counter_service
        #  .get_pushes_count(token))
        has_quota = subscriber_pushes < limit
        last_bid_key = f"subscriber:{token}:last-bid-at"
        try:
            last_bid_time = int(redis_client.get(last_bid_key))
        except TypeError:
            last_bid_time = None
        if last_bid_time:
            time_passed = time.time() - last_bid_time
            time_passed_enough = time_passed > (bid_interval * 60)
            logger.debug("SubscriberProcessorService.process_subscriber: "
                         f"passed time since last bid {time_passed}")
        else:
            time_passed_enough = True
        if has_quota and time_passed_enough:
            if settings.SSP_VERSION == 1:
                logger.debug("process_subscriber: queue_ref.tell")
                queue_ref.tell(payload)
            else:
                logger.debug("process_subscriber: telling to ssp actor")
                ssp_ref.tell(payload)
            # self.queue.publish.call_async(payload)
            redis_client.set(last_bid_key, int(time.time()), ex=DAY_SECONDS)
        else:
            logger.info("SubscriberProcessorService.process_subscriber: "
                        f"for subscriber: {payload['subscriber']['_id']} "
                        f"has_quota={has_quota} "
                        f"time_passed_enough={time_passed_enough}")
        finish_time = time.time()
        logger.debug("SubscriberProcessorService.process_subscriber: "
                     "total execution time "
                     f"{(finish_time - start_time) * 1000}ms")
