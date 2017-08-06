import requests


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


# class CachedCabinet(object):

#     def __init__(self, cabinet, engine):
#         self.cabinet = cabinet
#         self.engine = engine

#     def __getattr__(self, method):
#         def wrapper(*args, **kwargs):
#             cached_value = self.engine.get(method)
#             if cached_value:
#                 return cached_value
#             else:
#                 new_value = getattr(self.cabinet, method)(*args, **kwargs)
#                 self.engine.set(method, cached_value)
#                 return new_value
#         return wrapper


# class RedisCache(object):

#     def __init__(self, client, prefix, ttl):
#         self.client = client
#         self.prefix = prefix
#         self.ttl = ttl

#     def set(self, key, value):
#         prefixed_key = f"{self.prefix}_{key}"
#         self.client.set(prefixed_key, value)
#         self.client.set_ttl(prefixed_key, self.ttl)

#     def get(self, key):
#         prefixed_key = f"{self.prefix}_{key}"
#         self.client.get(prefixed_key)


# cached_cabinet = CachedCabinet(
#     RedisCache(prefix="CABINET_CACHE", ttl=60),
#     cabinet)

# cached_cabinet.general()
