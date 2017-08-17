#### Usage

    import redis
    from cabinet import CachedCabinet, Cabinet, RedisEngine


    REDIS_URI = ""
    REDIS_POOL = redis.ConnectionPool.from_url(REDIS_URI)

    redis_client = redis.Redis(connection_pool=REDIS_POOL)

    cab = Cabinet("base_url")

    cached_cabinet = CachedCabinet(
        cab,
        RedisEngine(redis_client, prefix="CABINET_CACHE", ttl=5))

    cached_cabinet.general()
