import requests
from nameko.rpc import rpc, RpcProxy

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
        print("CampaignProcessorService.process_campaign: "
              f"processing campaign - {payload}")
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
        url = settings.CABINET_URL + "/api/general/"
        cabinet_settings = requests.get(url).json()
        volume = cabinet_settings["bids_volume"]
        start_hour = cabinet_settings["start_hour"]
        end_hour = cabinet_settings["end_hour"]
        hours_whitelist = list(range(start_hour, end_hour + 1))
        subscribers = (self.subscriber_service.get_subscribers(
            targetings,
            hours_whitelist,
            volume
        ))
        if not subscribers:
            print("CampaignProcessorService.process_campaign: "
                  f"no subscribers found for campaign: #{payload['id']}")
            return
        for subscriber in subscribers:
            (self.subscriber_processor_service.process_subscriber
             .call_async(dict(campaign=payload, subscriber=subscriber)))
        print("CampaignProcessorService.process_campaign: "
              f"for campaign #{payload['id']} "
              f"processed {len(subscribers)} subscribers")
