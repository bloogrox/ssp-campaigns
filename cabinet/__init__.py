import requests
import json


class Cabinet(object):

    def __init__(self, base_url):
        self.base_url = base_url

    def call(self, method_name):
        url = self.base_url + f"/api/{method_name}/"
        return requests.get(url, timeout=1).json()

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
            print(f'requesting from cache {method}')
            cached_value = self.engine.get(method)
            print(f'received from cache {cached_value}')
            if cached_value:
                print(f'returning cached value')
                return cached_value
            else:
                print(f'requesting from remote service {method}')
                new_value = getattr(self.cabinet, method)(*args, **kwargs)
                print(f'received from remote service {new_value}')
                self.engine.set(method, new_value)
                print(f'and returning {new_value}')
                return new_value
        return wrapper


class RedisEngine(object):

    def __init__(self, redis_client, prefix, ttl):
        self.redis_client = redis_client
        self.prefix = prefix
        self.ttl = ttl

    def set(self, key, value):
        prefixed_key = f"{self.prefix}_{key}"
        print(f'redis.set: {prefixed_key}={json.dumps(value)} '
              f'with ttl={self.ttl}')
        res = self.redis_client.set(prefixed_key, json.dumps(value),
                                    ex=self.ttl)
        print(f'redis.set: result {res}')

    def get(self, key):
        prefixed_key = f"{self.prefix}_{key}"
        print(f'redis.get: {prefixed_key}')
        value = self.redis_client.get(prefixed_key)
        print(f'redis.get: received {value}')
        if value:
            print(f"redis.get: returning {json.loads(value.decode('utf-8'))}")
            return json.loads(value.decode('utf-8'))
        print(f'redis.get: returning {value}')
        return value
