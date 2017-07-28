from nameko.rpc import rpc
import redis
from app import REDIS_POOL
from datetime import date


class StatsService:
    name = "stats_service"

    @rpc
    def get_pushes_total_count(self, campaign_id):
        client = redis.Redis(connection_pool=REDIS_POOL)
        value = client.get(f"stats:campaign:{campaign_id}:total-count")
        print("StatsService.get_pushes_total_count: "
              f"get total pushes count "
              f"for the campaign {campaign_id}")
        try:
            return int(value)
        except TypeError:
            return 0

    @rpc
    def get_pushes_daily_count(self, campaign_id):
        client = redis.Redis(connection_pool=REDIS_POOL)
        date_str = date.today().isoformat()
        value = client.get(f"stats:campaign:{campaign_id}:date:{date_str}")
        print("StatsService.get_pushes_daily_count: "
              f"get total pushes count for the campaign {campaign_id}")
        try:
            return int(value)
        except TypeError:
            return 0
