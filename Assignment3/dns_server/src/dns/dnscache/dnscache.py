import redis
import time
import struct
import logging

class DNSCache(object):

    def __init__(self):

        # Default setting localhost, 6379
        try:
            self._redis = redis.StrictRedis()
        except redis.ConnectionError:
            raise
        # For temp cahce saving 
        self._cache = []

    def set_cache(self, name, a_type_str, a_data, a_ttl):
        if not name[-1] == ".":
            name += "."

        # TODO ttl is just for fun
        data = struct.pack("!ii", a_ttl, int(time.time()))

        a_key = name + ":" + a_type_str
        
        # put into local cache
        # self._cache.
        return self._redis.set(a_key, a_data+data)

    def get_cache(self, name, a_type_str):
        if not name[-1] == ".":
            name += "."
        a_key = name + ":" + a_type_str

        data =  self._redis.get(a_key)
        if not data:
            return None
        
        ttl, a_time = struct.unpack("!ii", data[-8:])
        logging.debug("TTL and time is {}, {}".format(ttl, a_time))
        # TTL is endding
        if int(time.time()) - a_time > ttl:
            self._redis.set("a_key", None)
            return None
        else:
            return data[:-8]


# FOR global use cache
cache = DNSCache()


if __name__ == "__main__":
    red = DNSCache()
    print(red.set_cache("baidu.com", "NS", b"\x00\x00\x01", 3))
    time.sleep(2)
    print(red.get_cache("baidu.com", "NS"))

