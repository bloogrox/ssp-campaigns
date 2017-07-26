from nameko.rpc import rpc
from app import campaigns


# @todo #1:30min rewrite to a wrapper module for campaign api
#  this doesn't need to be a service
class CampaignService:
    name = "campaign_service"

    @rpc
    def get_campaigns(self):
        print("CampaignService.get_campaigns: getting active campaigns")
        return campaigns
