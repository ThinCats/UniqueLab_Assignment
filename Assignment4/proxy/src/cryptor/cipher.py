
"""
This py is for algorithms of cipher
"""

import hashlib
import threading

md5 = hashlib.md5()
lock = threading.Lock()

class RC4(object):
    
    def __init__(self, user_key):
        if type(user_key) is str:
            user_key = bytes(user_key, "ascii")

        md5.update(user_key)
        # key will not change 
        key = md5.digest()

        # This
        self._status_vec = [i for i in range(256)]
        # temp will not change
        temp_vec = [key[i%len(key)] for i in range(256)]

        # First arrange status_vec
        j = 0
        for i in range(256):
            j = (j + self._status_vec[i] + temp_vec[i]) % 256
            self._status_vec[i], self._status_vec[j] = self._status_vec[j], self._status_vec[i] 

        # make it unchangable
        self._status_vec = tuple(self._status_vec)

        # cache is a dict {[data_len]:[key_stream]}
        # To accelerate decrpting
        self._cache = {}
    
    def _gen_keystream(self, data_len):
        """
        Return encrypted data
        """
        # Use status
        status = list(self._status_vec)
        key_stream = []
        i = 0
        j = 0
        for r in range(data_len):
            i = (i+1) % 256
            j = (j+status[i]) % 256
            status[i], status[j] = status[j], status[i]
            t = (status[i] + status[j] ) % 256
            # gen key stream
            key_stream.append(status[t])
        return key_stream

    def _data_xor_key(self, data_in):
        data_out_lst = []
        # Try to get keystream from cache
        key = self._cache.get(len(data_in), None)
        print(key)
        if not key:
            # Cache not exist:
            key = self._gen_keystream(len(data_in))
            # Saving in cache
            lock.acquire()
            try:
                self._cache[len(data_in)] = key
            finally:
                lock.release()
            
        for i in range(len(key)):
            data_out_lst.append(data_in[i] ^ key[i])
        
        return bytes(data_out_lst)

    def decrypt(self, data_in):
        return self._data_xor_key(data_in)

    def encrypt(self, data_in):
        return self._data_xor_key(data_in)

if __name__ == "__main__":
    test = RC4("hello_kitty")
    encr = test.encrypt(b"xxx")
    print(encr)
    print(test.decrypt(encr))