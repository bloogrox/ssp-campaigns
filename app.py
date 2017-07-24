import json
import redis
import pymongo
import pika
import pika_pool
import requests
from geolite2 import geolite2
import pycountry
import json
from nameko.rpc import rpc, RpcProxy
from nameko.timer import timer
from elasticsearch import Elasticsearch
from elasticsearch import helpers


import settings


REDIS_POOL = redis.ConnectionPool.from_url(settings.REDIS_URI)

mongo_client = pymongo.MongoClient(settings.MONGO_URI)
mongo_database = mongo_client.get_default_database()
es = Elasticsearch([settings.ELASTIC_URI])

# 'amqp://guest:guest@localhost:5672/
pika_params = pika.URLParameters(
    settings.EXT_AMQP_URI + '?'
    'socket_timeout=10&'
    'connection_attempts=2'
)

rmq_pool = pika_pool.QueuedPool(
    create=lambda: pika.BlockingConnection(parameters=pika_params),
    max_size=10,
    max_overflow=10,
    timeout=10,
    recycle=3600,
    stale=45,
)


# country_whitelist = []
country_blacklist = ["VNM", "IND", "IDN", "PHL", "ROU", "COL", "THA", "MEX",
                     "MYS", "MAR", "HUN", "ESP", "ITA", "PAK", "TUR", "TWN",
                     "CHL", "GEO", "PER", "CZE", "AZE", "SRB", "KAZ"]


campaigns = [
    {
        "id": 1,
        "dsp_id": 1,
        "total_limit": 100000,
        "daily_limit": 1000,
        "targetings": [
            {
                "field": "country",
                "operator": "NOT IN",
                "value": country_blacklist
            }
        ]
    }
]


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


# @todo #1:30min rewrite to a wrapper module for campaign api
#  this doesn't need to be a service
class CampaignService:
    name = "campaign_service"

    @rpc
    def get_campaigns(self):
        print("CampaignService.get_campaigns: getting active campaigns")
        return campaigns


class StatsService:
    name = "stats_service"

    @rpc
    def get_pushes_total_count(self, campaign_id):
        # @todo #1:30min perform a call to Druid
        print("StatsService.get_pushes_total_count: "
              f"get total pushes count for the campaign {campaign_id}")


class SubscriberService:
    name = "subscriber_service"

    @rpc
    def get_subscribers(self, filters, limit):
        print("SubscriberService.get_subscribers: getting subscribers")
        pipeline = [
            # {"country_code": {"$not": {"$in": ["USA"]}}}
            # {"$project": {
            #     "_id": 0,
            #     "uid": 1
            # }},
            {"$match": filters},
            {"$sample": {"size": limit}}
        ]
        try:
            return list(mongo_database.subscribers.aggregate(pipeline))
        except Exception as e:
            print("SubscriberService.get_subscribers: Exception " + str(e))

    @rpc
    def update_subscriber(self, document):
        try:
            sid = document['_id']
            document.pop('_id', None)
            es.index(index='subscribers', doc_type="post", id=sid, body=document)
            print("SubscriberService.update_subscriber: "
                  "replace_one done successfully for " + document["_id"])
        except Exception as e:
            print("SubscriberService.update_subscriber: "
                  "Exception " + str(e))


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
        # total_count = self.stats_service.get_pushes_total_count()
        # targetings = payload["targetings"]
        # if total_count >= total_limit:
        #     print("CampaignProcessorService.process_campaign: "
        #           f"campaign limit exceeded: {payload}")
        #     return None

        # @todo #1:15min send targetings data to receive needed auditory

        filters = {"country": {"$not": {"$in": country_blacklist}}}
        limit = 1
        subscribers = self.subscriber_service.get_subscribers(filters, limit)
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


class Queue:
    name = "queue"

    @rpc
    def publish(self, payload):
        with rmq_pool.acquire() as cxn:
            try:
                cxn.channel.basic_publish(
                    body=json.dumps(payload),
                    exchange='',
                    routing_key='sell-imp',
                    properties=pika.BasicProperties(
                        content_type='plain/text'
                    )
                )
                print(f"Queue.publish published: {payload['_id']}")
            except Exception as e:
                print(f"Queue.publish exception: {e}")


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
        # @todo #1:15min get limit-per-user value from global settings

        # @todo #11:30min filter user by timezone
        print("SubscriberProcessorService.process_subscriber: "
              f"processing subscriber: {payload}")
        if self.counter_service.get_pushes_count("token") <= 3:
            self.queue.publish.call_async(payload)
        else:
            print("SubscriberProcessorService.process_subscriber: "
                  f"limit for subscriber: {payload} exceeded")


class Timer:
    name = "timer_service"

    campaigns_runner_service = RpcProxy("campaigns_runner_service")
    syncer_service = RpcProxy("syncer_service")

    @timer(interval=5)
    def run_campaigns(self):
        print("tick")
        self.campaigns_runner_service.run.call_async()


class SubscriberRemoteStorageService:
    name = "subscriber_remote_storage_service"

    base_url = "http://push-w.ru/api/"

    @rpc
    def get_total_count(self):
        url = f"{self.base_url}subscribers"
        params = {"per_page": 1}
        headers = {
            "X-Auth-Token": settings.PUSHW_AUTH_TOKEN,
            "X-Auth-Key": settings.PUSHW_AUTH_KEY
        }
        resp = requests.get(url, params=params, headers=headers)
        return resp.json()["total_count"]

    @rpc
    def subscribers(self, per_page, page_number):
        url = f"{self.base_url}subscribers"
        params = {
            "per_page": per_page,
            "pgno": page_number}
        headers = {
            "X-Auth-Token": settings.PUSHW_AUTH_TOKEN,
            "X-Auth-Key": settings.PUSHW_AUTH_KEY
        }
        resp = requests.get(url, params=params, headers=headers)
        return resp.json()["lines"]


# @todo #25:60min create api wrapper for remote subscribers
#  and use it in SubscriberRemoteStorageService


class SyncerService:
    name = "syncer_service"

    subscriber_remote_storage_service = (
        RpcProxy("subscriber_remote_storage_service"))
    syncer_page_processor_service = RpcProxy("syncer_page_processor_service")

    @rpc
    def run(self):
        total_count = self.subscriber_remote_storage_service.get_total_count()
        print(f"SyncerService.run: total count is {total_count}")
        for page_number in range((total_count // 1000) + 1):
            (self.syncer_page_processor_service.process_page
             .call_async(1000, page_number))


class SyncerPageProcessorService:
    name = "syncer_page_processor_service"

    syncer_subscriber_augmentor_service = (
        RpcProxy("syncer_subscriber_augmentor_service"))
    subscriber_remote_storage_service = (
        RpcProxy("subscriber_remote_storage_service"))

    @rpc
    def process_page(self, limit, page_number):
        subscribers = (self.subscriber_remote_storage_service
                       .subscribers(limit, page_number))
        print("SyncerService.process_page: "
              f"page {page_number} loaded")
        for subscriber in subscribers:
            (self.syncer_subscriber_augmentor_service.augment
             .call_async(subscriber))


class SyncerSubscriberAugmentorService:
    name = "syncer_subscriber_augmentor_service"

    subscriber_service = RpcProxy("subscriber_service")

    @rpc
    def augment(self, subscriber):
        reader = geolite2.reader()
        ip_info = reader.get(subscriber["ip_address"])

        alpha_2 = ip_info["country"]["iso_code"]
        alpha_3 = pycountry.countries.get(alpha_2=alpha_2).alpha_3

        subscriber["timezone"] = ip_info["location"]["time_zone"]
        subscriber["country"] = alpha_3

        self.subscriber_service.update_subscriber.call_async(subscriber)

        print("SyncerSubscriberAugmentorService.augment: "
              "successfully augmented " + subscriber["_id"])
