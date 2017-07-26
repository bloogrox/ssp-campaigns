from nameko.rpc import rpc, RpcProxy
from app import campaigns


class CampaignsRunnerService:
    name = "campaigns_runner_service"

    campaign_service = RpcProxy("campaign_service")
    campaign_processor_service = RpcProxy("campaign_processor_service")

    @rpc
    def run(self):
        # campaigns = self.campaign_service.get_campaigns()
        for campaign in campaigns:
            print(f"CampaignsRunnerService.run: sending campaign: {campaign}"
                  " for processing.")
            (self.campaign_processor_service.process_campaign
             .call_async(campaign))
