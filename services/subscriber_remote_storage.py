import requests
from nameko.rpc import rpc
import settings


# @todo #25:60min create api wrapper for remote subscribers
#  and use it in SubscriberRemoteStorageService


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
