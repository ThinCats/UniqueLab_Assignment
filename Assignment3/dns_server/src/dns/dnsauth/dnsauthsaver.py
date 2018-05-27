import redis
import time
import struct
import logging

class DNSAuthSaver(object):

    def __init__(self):

        # Default setting localhost, 6379
        try:
            # Use db 1 to save record
            self._redis = redis.StrictRedis(db=1)
        except redis.ConnectionError:
            raise
        # For temp cahce saving 
        self._cache = []

    def save_record(self, name, a_type_str, a_data):
        if not name[-1] == ".":
            name += "."

        a_key = name.lower() + ":" + a_type_str
        
        # put into local cache
        # self._cache.
        return self._redis.set(a_key, a_data)

    def get_record(self, name, a_type_str):
        if not name[-1] == ".":
            name += "."
        a_key = name.lower() + ":" + a_type_str
        data =  self._redis.get(a_key)

        return data


# FOR global use cache
saver = DNSAuthSaver()


if __name__ == "__main__":
    red = DNSAuthSaver()
    print(red.save_record("baidu.com", "NS", b"\x00\x00\x01"))
    # time.sleep(2)
    print(red.get_record("baidu.com", "NS"))

