
"""
This py is for algorithms of cipher
"""

import hmac
import threading

lock = threading.Lock()
salt = b"Salty_thing"

class RC4(object):
    
    def __init__(self, user_key, message=salt):
        if type(user_key) is str:
            user_key = bytes(user_key, "ascii")

        if type(message) is str:
            message = bytes(message, "ascii")
        # For callback info
        self.user_key = user_key
        self.message = message

        h = hmac.new(user_key, message, digestmod="MD5")
        # key will not change 
        key = h.digest()

        # This
        self._status = [i for i in range(256)]
        # temp will not change
        temp_vec = [key[i%len(key)] for i in range(256)]

        # First arrange status_vec
        j = 0
        for i in range(256):
            j = (j + self._status[i] + temp_vec[i]) % 256
            self._status[i], self._status[j] = self._status[j], self._status[i] 

        # This is simple replacement algo
        # Gen word->pass table
        self._word_pass = dict([(key, self._status[key]) for key in range(len(self._status))])
        self._pass_word = dict([(val, key) for (key, val) in self._word_pass.items()])



    def _table_key(self, data_in, word_list):
        data_out = []
        for ch in data_in:
            data_out.append(word_list[ch])
        return bytes(data_out)

    def decrypt(self, data_in):
        return self._table_key(data_in, self._pass_word)

    def encrypt(self, data_in):
        return self._table_key(data_in, self._word_pass)


if __name__ == "__main__":
    test = RC4("1234")
    encr = test.encrypt(b"xxx")
    print(encr)
    print(test.decrypt(encr))