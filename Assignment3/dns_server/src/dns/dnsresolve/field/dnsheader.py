import struct
import random

if __package__:
    from . import codes
    from . import dnsflag
else:
    import codes, dnsflag


"""
This is for setting up the header
"""


class DNSHeader(object):

    def __init__(self, id=None, flag=0, data=None):
        self._id = id
        self._flag = flag
        self._qdcount = 0
        self._ancount = 0
        self._nscount = 0
        self._arcount = 0
        self._data = data

    def add_id(self, id=None):
        if id == None:
           id = random.randrange(1, 65535)

        self._id = id
    def modify_id(self, id):
        if id == None:
            raise ValueError("[Err] id can't be None")
        self._id = id
    
    def add_flag(self, qr, opcode, aa, tc, rd, ra, ad, rcode, z=0, cd=1):
        self._flag = dnsflag.pack_flag(self._flag, qr, opcode, aa, tc, rd, ra, ad, rcode)
    
    def modify_flag(self, **kw):
        for key, val in kw.items():
            self._flag = dnsflag.setFunctions[key.lower()](self._flag, val)

    # Read flag mapping item
    # item = qr , read qr in flag
    def read_flag(self, item):
        return dnsflag.getFunctions[item](self._flag)

    @property
    def flag(self):
        return self._flag
            
    def add_qdcount(self, qdcount):
        self._qdcount = qdcount
    
    def add_ancount(self, ancount):
        self._ancount = ancount

    def add_nscount(self, nscount):
        self._nscount = nscount

    def add_arcount(self, arcount):
        self._arcount = arcount

    def pack(self):
        self._data = struct.pack("!HHHHHH", self._id, self._flag, self._qdcount, self._ancount, self._nscount, self._arcount)

    @property
    def data(self):
        return self._data
    @property
    def id(self):
        return self._id
    @property
    def count(self):
        return (self._qdcount, self._ancount, self._nscount, self._arcount)

    @classmethod
    def unpack(cls, a_data):
        #return struct.unpack
        # return struct.unpack("!HHHHHH", a_data)
        out = struct.unpack("!HHHHHH", a_data)
        return cls(out[0], out[1])

    def __str__(self):
        return str(self._data)



if __name__ == "__main__":
    a_header = DNSHeader()
    a_header.add_id()
    a_header.add_flag(codes.QR["query"], codes.OPCODE["query"], 0, 1, 1, 1, 0, codes.RCODE["NoError"])
    a_header.add_qdcount(0)
    a_header.add_ancount(0)
    a_header.add_arcount(0)
    a_header.add_arcount(0)
    a_header.pack()
    
    print(a_header.data)

    print(a_header.unpack(a_header.data).flag)

    a_header.modify_flag(aa = 1, tc = 0, qr = 1)
    a_header.pack()