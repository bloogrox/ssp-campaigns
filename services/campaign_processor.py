from nameko.rpc import rpc, RpcProxy
from app import country_whitelist


class CampaignProcessorService:
    """Process campaign and fetch subscribers
    """
    name = "campaign_processor_service"

    stats_service = RpcProxy("stats_service")
    subscriber_service = RpcProxy("subscriber_service")
    subscriber_processor_service = RpcProxy("subscriber_processor_service")

    @rpc
    def process_campaign(self, payload):
        print("CampaignProcessorService.process_campaign: "
              f"processing campaign - {payload}")
        # @todo #1:15min daily count check

        total_limit = payload['total_limit']
        total_count = self.stats_service.get_pushes_total_count(payload["id"])
        daily_count = self.stats_service.get_pushes_daily_count(payload["id"])

        # targetings = payload["targetings"]
        if total_count >= total_limit or daily_count >= total_limit:
            print("CampaignProcessorService.process_campaign: "
                  f"campaign limit exceeded: {payload}")
            return None

        # @todo #1:15min send targetings data to receive needed auditory

        limit = 1
        subscribers = (self.subscriber_service
                       .get_subscribers(country_whitelist, limit))
        if not subscribers:
            print("CampaignProcessorService.process_campaign: "
                  f"no subscribers found for campaign: #{payload['id']}")
            return
        for subscriber in subscribers:
            (self.subscriber_processor_service.process_subscriber
             .call_async(subscriber))
        print("CampaignProcessorService.process_campaign: "
              f"for campaign #{payload['id']} "
              f"processed {len(subscribers)} subscribers")
