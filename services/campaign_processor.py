import time
import redis
from nameko.rpc import rpc, RpcProxy
from cabinet import Cabinet, CachedCabinet, RedisEngine
from app import REDIS_POOL, logger
import settings


class CampaignProcessorService:
    """Process campaign and fetch subscribers
    """
    name = "campaign_processor_service"

    stats_service = RpcProxy("stats_service")
    subscriber_service = RpcProxy("subscriber_service")
    subscriber_processor_service = RpcProxy("subscriber_processor_service")

    @rpc
    def process_campaign(self, payload):
        logger.info("CampaignProcessorService.process_campaign: "
                    f"processing campaign - {payload}")
        start_time = time.time()
        # @todo #1:15min daily count check

        # total_limit = payload['total_limit']
        # total_count = (self.stats_service
        #                .get_pushes_total_count(payload["id"]))
        # daily_count = (self.stats_service
        #                .get_pushes_daily_count(payload["id"]))
        # if total_count >= total_limit or daily_count >= total_limit:
        #     print("CampaignProcessorService.process_campaign: "
        #           f"campaign limit exceeded: {payload}")
        #     return None

        targetings = payload["targetings"]
        redis_client = redis.Redis(connection_pool=REDIS_POOL,
                                   socket_timeout=1)
        cab = Cabinet(settings.CABINET_URL)
        cached_cabinet = CachedCabinet(
            cab,
            RedisEngine(redis_client, prefix="CABINET_CACHE", ttl=30))
        cabinet_settings = cached_cabinet.general()
        start_hour = cabinet_settings["start_hour"]
        end_hour = cabinet_settings["end_hour"]
        hours_whitelist = list(range(start_hour, end_hour + 1))
        volume = payload["subscriber_selection_size"]
        subscribers = (self.subscriber_service.get_subscribers(
            targetings,
            hours_whitelist,
            volume
        ))
        if not subscribers:
            logger.info("CampaignProcessorService.process_campaign: "
                        f"no subscribers found for campaign: #{payload['id']}")
            return
        for subscriber in subscribers:
            time1 = time.time()
            (self.subscriber_processor_service.process_subscriber
             .call_async(dict(campaign=payload, subscriber=subscriber)))
            time2 = time.time()
            logger.debug("CampaignProcessorService.process_campaign: "
                         "called process_subscriber in "
                         f"{int((time2 - time1) * 1000)}ms")
        end_time = time.time()
        logger.info("CampaignProcessorService.process_campaign: "
                    f"for campaign #{payload['id']} "
                    f"processed {len(subscribers)} subscribers "
                    f"in {(end_time - start_time) * 1000}ms")
