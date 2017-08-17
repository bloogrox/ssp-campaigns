import requests
import json


class Cabinet(object):

    def __init__(self, base_url):
        self.base_url = base_url

    def call(self, method_name):
        url = self.base_url + f"/api/{method_name}/"
        return requests.get(url).json()

    def general(self):
        return self.call('general')

    def campaigns(self):
        return self.call('campaigns')


class CachedCabinet(object):

    def __init__(self, cabinet, engine):
        self.cabinet = cabinet
        self.engine = engine

    def __getattr__(self, method):
        def wrapper(*args, **kwargs):
            cached_value = self.engine.get(method)
            if cached_value:
                return cached_value
            else:
                new_value = getattr(self.cabinet, method)(*args, **kwargs)
                self.engine.set(method, new_value)
                return new_value
        return wrapper


class RedisEngine(object):

    def __init__(self, redis_client, prefix, ttl):
        self.redis_client = redis_client
        self.prefix = prefix
        self.ttl = ttl

    def set(self, key, value):
        prefixed_key = f"{self.prefix}_{key}"
        self.redis_client.set(prefixed_key, json.dumps(value), ex=self.ttl)

    def get(self, key):
        prefixed_key = f"{self.prefix}_{key}"
        value = self.redis_client.get(prefixed_key)
        if value:
            return json.loads(value.decode('utf-8'))
        return value
