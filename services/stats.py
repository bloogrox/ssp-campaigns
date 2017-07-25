from nameko.rpc import rpc


class StatsService:
    name = "stats_service"

    @rpc
    def get_pushes_total_count(self, campaign_id):
        # @todo #1:30min perform a call to Druid
        print("StatsService.get_pushes_total_count: "
              f"get total pushes count for the campaign {campaign_id}")
