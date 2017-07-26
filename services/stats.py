from nameko.rpc import rpc
import redis
from app import REDIS_POOL
from datetime import date

class StatsService:
    name = "stats_service"

    @rpc
    def get_pushes_total_count(self, campaign_id):
        # @todo #1:30min perform a call to Druid
        client = redis.Redis(connection_pool=REDIS_POOL)
        value = client.get(f"stats:campaign:{campaign_id}:total-count")
        print("StatsService.get_pushes_total_count: "
              f"get total pushes count for the campaign {campaign_id}")
        return value

    @rpc
    def get_pushes_daily_count(self, campaign_id):
        client = redis.Redis(connection_pool=REDIS_POOL)
        value = client.get(f"stats:campaign:{campaign_id}:date:{date.today().isoformat()}")
        print("StatsService.get_pushes_daily_count: "
              f"get total pushes count for the campaign {campaign_id}")
        return value
