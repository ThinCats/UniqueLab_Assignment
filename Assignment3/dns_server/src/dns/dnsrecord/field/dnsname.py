
import struct
"""
DNSName for dealing with name
name is the set of lables
TODO: parse the encoded name
TODO: use compress to encode the name

"""
class DNSName(object):

    def __init__(self):
        #self.encoded_name = b""
        pass

    # No compressed
    @classmethod
    def encode(cls, a_name):
        if type(a_name) == str:
            a_name = bytes(a_name, "ascii")

        if(len(a_name) > 253):
            raise ValueError("Name is more than 253 characters")
        # a.com -> ("a", "com")
        lables = a_name.split(b".")
        out = []
        for a_lable in lables:
            if(len(a_lable) > 63):
                raise ValueError("Lable %s is more than 63 characters" %(a_lable))
            out.append(struct.pack("!B", len(a_lable)))
            out.append(a_lable)
        out.append(b"\0")
        return b"".join(out)

   # def get_name(self):
   #     return self.encoded_name

    @classmethod
    def parse(self, a_bytes):
        pass

if __name__ == "__main__":
    print(DNSName.encode(b"www.baidu.com"))