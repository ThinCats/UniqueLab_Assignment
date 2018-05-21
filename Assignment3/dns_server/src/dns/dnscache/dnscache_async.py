
import aioredis
import asyncio

class DNSCache(object):

    def __init__(self):
        # auto connecting
        self._redis = None

        # For local temp cache
        # later will upload to redis
        self._cache = None

    async def connect(self):
        self._redis = await aioredis.create_redis_pool(
            "redis://localhost"
        )
    async def set_cache(self, name, a_type_str, data):
        if not name[-1] == ".":
            name += "."
        
        a_key = name + ":" + a_type_str.upper()
        a_val = data
        # TODO fix the bytes data
        await self._redis.set(a_key, a_val)
        
    async def get_cache(self, name, a_type_str):
        """
        Return raw bytes data
        """
        # Normalize
        if not name[-1] == ".":
            name += "."

        a_key = name + ":" + a_type_str.upper()
        a_data = await self._redis.get(a_key)
        print(a_data)
        return a_data

if __name__ == "__main__":
    cache = DNSCache()

    loop = asyncio.get_event_loop()
    loop_mis = asyncio.get_event_loop()
    loop.run_until_complete(cache.connect())
    loop_mis.run_until_complete(cache.set_cache("baidu.com", "NS", b"\x00\x03"))
    asyncio.get_event_loop().run_until_complete(cache.get_cache("baidu.com", "NS"))
    cache.get_cache("Ba", "Sda")