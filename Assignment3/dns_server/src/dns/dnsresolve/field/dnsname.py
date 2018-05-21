
import struct
"""
DNSName for dealing with name
name is the set of lables
TODO: parse the encoded name
TODO: use compress to encode the name

"""

if __package__:
    from .bitsopr import get_bits, set_bits, print_bits
else:
    from bitsopr import get_bits

class DNSName(object):

    def __init__(self):
        #self.encoded_name = b""
        pass

    # No compressed
    @classmethod
    def encode(cls, a_name):
        if a_name == None:
            return b""
        
        if not type(a_name) == list:
            if type(a_name) == str:
                a_name = bytes(a_name, "ascii")

            if(len(a_name) > 253):
                raise ValueError("Name is more than 253 characters")
            # a.com -> ("a", "com")
            lables = a_name.split(b".")
        else:
            lables = a_name
        # ROOT server
        out = []
        for a_lable in lables:
            if a_lable == b"":
                continue
            if(len(a_lable) > 63):
                raise ValueError("Lable %s is more than 63 characters" %(a_lable))
            out.append(struct.pack("!B", len(a_lable)))
            out.append(a_lable)
        out.append(b"\0")
        
        return b"".join(out)

    # For decode lables that is compressed
    # But temporaily unsuppor for widecard
    @classmethod
    def decode(cls, a_lables, all_data):
        pass

   # def get_name(self):
   #     return self.encoded_name

    @classmethod
    def parse(self, a_bytes):
        pass

if __name__ == "__main__":
    
    raw_data =  b"\xac\x78\x81\x80\x00\x01\x00\x03\x00\x01\x00\x00\x02\x64\x63\x08" \
b"\x73\x65\x72\x76\x69\x63\x65\x73\x0c\x76\x69\x73\x75\x61\x6c\x73" \
b"\x74\x75\x64\x69\x6f\x03\x63\x6f\x6d\x00\x00\x1c\x00\x01\xc0\x0c" \
b"\x00\x05\x00\x01\x00\x00\x00\xe6\x00\x23\x02\x64\x63\x13\x61\x70" \
b"\x70\x6c\x69\x63\x61\x74\x69\x6f\x6e\x69\x6e\x73\x69\x67\x68\x74" \
b"\x73\x09\x6d\x69\x63\x72\x6f\x73\x6f\x66\x74\xc0\x25\xc0\x3a\x00" \
b"\x05\x00\x01\x00\x00\x00\x0f\x00\x17\x02\x64\x63\x0e\x74\x72\x61" \
b"\x66\x66\x69\x63\x6d\x61\x6e\x61\x67\x65\x72\x03\x6e\x65\x74\x00" \
b"\xc0\x69\x00\x05\x00\x01\x00\x00\x00\x1e\x00\x1c\x10\x73\x65\x61" \
b"\x2d\x62\x72\x65\x65\x7a\x69\x65\x73\x74\x2d\x69\x6e\x08\x63\x6c" \
b"\x6f\x75\x64\x61\x70\x70\xc0\x7b\xc0\x9d\x00\x06\x00\x01\x00\x00" \
b"\x00\x04\x00\x41\x04\x70\x72\x64\x31\x0e\x61\x7a\x75\x72\x65\x64" \
b"\x6e\x73\x2d\x63\x6c\x6f\x75\x64\xc0\x7b\x06\x6d\x73\x6e\x68\x73" \
b"\x74\x09\x6d\x69\x63\x72\x6f\x73\x6f\x66\x74\x03\x63\x6f\x6d\xc0" \
b"\x9d\x7d\xb0\x66\x74\x00\x00\x03\x84\x00\x00\x01\x2c\x00\x09\x3a" \
b"\x80\x00\x00\x00\x3c"

    res = DNSName()
    print(res.encode("www.baidu.com."))
    print(res.encode(""))
    print(res.encode("."))