import redis
import pymongo
import random

from nameko.rpc import rpc, RpcProxy
from nameko.timer import timer


# @todo #12:15min use URI from env
REDIS_POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)

mongo_client = pymongo.MongoClient("mongodb://127.0.0.1:27017/db")


class CampaignsRunnerService:
    name = "campaigns_runner_service"

    campaign_service = RpcProxy("campaign_service")
    campaign_processor_service = RpcProxy("campaign_processor_service")

    @rpc
    def run(self):
        campaigns = self.campaign_service.get_campaigns()
        for campaign in campaigns:
            print("CampaignsRunnerService.run: sending campaign: " + str(campaign) + " for processing.")
            self.campaign_processor_service.process_campaign.call_async(campaign)


# @todo #1:30min rewrite to a wrapper module for campaign api 
#  this doesn't need to be a service
class CampaignService:
    name = "campaign_service"

    @rpc
    def get_campaigns(self):
        print("CampaignService.get_campaigns: getting active campaigns")
        return [
            {"id": 1, "total_limit": 60}, 
            {"id": 2, "total_limit": 80} 
        ]


class StatsService:
    name = "stats_service"

    @rpc
    def get_pushes_total_count(self, campaign_id):
        # @todo #1:30min perform a call to Druid
        print("StatsService.get_pushes_total_count: get total pushes count for the campaign %d" % campaign_id)
        return random.randint(50, 100)


class SubscriberService:
    name = "subscriber_service"

    @rpc
    def get_subscribers(self, filters, limit):
        print("SubscriberService.get_subscribers: getting subscribers")
        db = mongo_client.db
        pipeline = [
            # {"country_code": {"$not": {"$in": ["USA"]}}}
            {"$match": filters},
            {"$sample": {"size": limit}}
        ]
        return list(db.subscribers.aggregate(pipeline))


class CampaignProcessorService:
    """Process campaign and fetch subscribers
    """
    name = "campaign_processor_service"

    stats_service = RpcProxy("stats_service")
    subscriber_service = RpcProxy("subscriber_service")
    subscriber_processor_service = RpcProxy("subscriber_processor_service")

    @rpc
    def process_campaign(self, payload):
        print("CampaignProcessorService.process_campaign: processing campaign - %s" % payload)
        # @todo #1:15min daily count check
        total_limit = payload['total_limit']
        total_count = self.stats_service.get_pushes_total_count(payload["id"])
        # targetings = payload["targetings"]
        if total_count >= total_limit:
            print("CampaignProcessorService.process_campaign: campaign limit exceeded: %s" % payload)
            return None

        # @todo #1:15min send targetings data to receive needed auditory
        subscribers = self.subscriber_service.get_subscribers({})
        for subscriber in subscribers:
            self.subscriber_processor_service.process_subscriber.call_async(subscriber)
        print("CampaignProcessorService.process_campaign: campaign: " + str(payload) + " - processed")


class Queue:
    name = "queue"

    @rpc
    def publish(self, payload):
        # @todo #1:15min connect to rabbitmq
        # @todo #1:15min publish to sell-imp queue
        print("Queue.publish: published: " + str(payload))


class CounterService:
    name = "counter_service"

    @rpc
    def get_pushes_count(self, token):
        print("CounterService.get_pushes_count: requesting push count")
        client = redis.Redis(connection_pool=REDIS_POOL)
        value = client.get(f"subscriber.pushes.count:{token}")
        try:
            return int(value)
        except TypeError:
            # If None returned
            return 0


class SubscriberProcessorService:
    name = "subscriber_processor_service"

    counter_service = RpcProxy("counter_service")
    queue = RpcProxy("queue")

    @rpc
    def process_subscriber(self, payload):
        """
        @todo #1:15min get limit-per-user value from global settings
        """
        print("SubscriberProcessorService.process_subscriber: processing subscriber: " + str(payload))
        if self.counter_service.get_pushes_count("token") <= 3:
            self.queue.publish.call_async(payload)
        else:
            print("SubscriberProcessorService.process_subscriber: limit for subscriber: %s exceeded" % payload)


class Timer:
    name = "timer_service"

    campaigns_runner_service = RpcProxy("campaigns_runner_service")

    @timer(interval=1)
    def run_campaigns(self):
        print("tick")
        self.campaigns_runner_service.run.call_async()
