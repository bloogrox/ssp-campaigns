from nameko.rpc import rpc, RpcProxy
import pycountry
from geolite2 import geolite2
import datetime
import pytz


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
        sub_tz = pytz.timezone(subscriber["timezone"])
        subscriber["timezone-offset"] = (datetime.datetime.now(sub_tz)
                                         .utcoffset().seconds // 3600)
        self.subscriber_service.update_subscriber.call_async(subscriber)

        print("SyncerSubscriberAugmentorService.augment: "
              "successfully augmented " + subscriber["_id"])
