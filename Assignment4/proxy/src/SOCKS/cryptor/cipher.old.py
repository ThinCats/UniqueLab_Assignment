
"""
This py is for algorithms of cipher
"""

import hmac
import threading

lock = threading.Lock()
salt = b"Salty_thing"

class RC4(object):
    
    def __init__(self, user_key):
        if type(user_key) is str:
            user_key = bytes(user_key, "ascii")

        h = hmac.new(user_key, salt, digestmod="MD5")
        # key will not change 
        key = h.digest()

        # This
        self._status_vec = [i for i in range(256)]
        # temp will not change
        temp_vec = [key[i%len(key)] for i in range(256)]

        # First arrange status_vec
        j = 0
        for i in range(256):
            j = (j + self._status_vec[i] + temp_vec[i]) % 256
            self._status_vec[i], self._status_vec[j] = self._status_vec[j], self._status_vec[i] 

        # To accelerate decrpting
        # Cache is a key [1, 2, 3...]
        self._key_stream = []
        # Save last keystream index i and j to accelerate gen key
        self._index = [0, 0]
        # Save last status
        self._status = self._status_vec[:]

        # This is simple replacement algo
        # Gen word->pass table
        self._word_pass = dict([(key, self._status[key]) for key in range(len(self._status))])
        self._pass_word = dict([(val, key) for (key, val) in self._word_pass.items()])

    def _gen_keystream(self, data_len):
        """
        Return encrypted data
        """
        # Use status
        
        i, j = self._index
        # Regen from last status
        for r in range(len(self._key_stream), data_len):
            i = (i+1) % 256
            j = (j+self._status[i]) % 256
            self._status[i], self._status[j] = self._status[j], self._status[i]
            t = (self._status[i] + self._status[j] ) % 256
            # gen key stream
            self._key_stream.append(self._status[t])
        
        self._index = [i, j]
        return self._key_stream

    def _data_xor_key(self, data_in):
        
        if len(data_in) == 0:
            return data_in
        
        data_out_lst = []

        # Key_stream < data_in length
        if len(data_in) > len(self._key_stream):
            # Regen key_stream
            lock.acquire()
            try:
                self._gen_keystream(len(data_in))
            finally:
                lock.release()
                pass
            
        for i in range(len(data_in)):
            data_out_lst.append(data_in[i] ^ self._key_stream[i])
        
        return bytes(data_out_lst)

    def _table_key(self, data_in, word_list):
        data_out = []
        for ch in data_in:
            data_out.append(word_list[ch])
        return bytes(data_out)

    def decrypt(self, data_in):
        # return self._data_xor_key(data_in)
        return self._table_key(data_in, self._pass_word)

    def encrypt(self, data_in):
        # return self._data_xor_key(data_in)
        return self._table_key(data_in, self._word_pass)


if __name__ == "__main__":
    test = RC4("1234")
    encr = test.encrypt(b"xxx")
    print(encr)
    print(test.decrypt(encr))