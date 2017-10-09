import redis
from nameko.rpc import rpc, RpcProxy
import settings
from cabinet import Cabinet, CachedCabinet, RedisEngine
from app import REDIS_POOL, logger


class CampaignsRunnerService:
    name = "campaigns_runner_service"

    campaign_processor_service = RpcProxy("campaign_processor_service")

    @rpc
    def run(self):
        redis_client = redis.Redis(connection_pool=REDIS_POOL)
        cab = Cabinet(settings.CABINET_URL)
        cached_cabinet = CachedCabinet(
            cab,
            RedisEngine(redis_client, prefix="CABINET_CACHE", ttl=5))
        campaigns = cached_cabinet.campaigns()
        logger.debug("CampaignsRunnerService.run: "
                     f"received active campaigns {campaigns}")
        for campaign in campaigns:
            (self.campaign_processor_service.process_campaign
             .call_async(campaign))
