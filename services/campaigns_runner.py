import requests
from nameko.rpc import rpc, RpcProxy
import settings


class CampaignsRunnerService:
    name = "campaigns_runner_service"

    campaign_processor_service = RpcProxy("campaign_processor_service")

    @rpc
    def run(self):
        url = settings.CABINET_URL + "/api/campaigns/"
        campaigns = requests.get(url).json()
        for campaign in campaigns:
            print(f"CampaignsRunnerService.run: sending campaign: {campaign}"
                  " for processing.")
            (self.campaign_processor_service.process_campaign
             .call_async(campaign))
