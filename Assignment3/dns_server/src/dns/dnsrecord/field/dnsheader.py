import struct
import random

import field.codes
import dnsflag
"""
This is for setting up the header
"""


class DNSHeader(object):

    def __init__(self):
        self._id = None
        self._flag = 0
        self._qdcount = 0
        self._ancount = 0
        self._nscount = 0
        self._arcount = 0
        self._data = None

    def add_id(self, id=None):
        if id == None:
           id = random.randrange(1, 65535)

        self._id = id
    
    def add_flag(self, qr, opcode, aa, tc, rd, ra, ad, rcode, z=0, cd=1):
        self._flag = dnsflag.pack_flag(self._flag, qr, opcode, aa, tc, rd, ra, ad, rcode)

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

    def get_data(self):
        return self._data
    
    def unpack(self):
        #return struct.unpack
        return struct.unpack("!HHHHHH", self._data)


if __name__ == "__main__":
    a_header = DNSHeader()
    a_header.add_id()
    a_header.add_flag(codes.QR["query"], codes.OPCODE["query"], 0, 1, 1, 1, 0, codes.RCODE["NoError"])
    a_header.add_qdcount(0)
    a_header.add_ancount(0)
    a_header.add_arcount(0)
    a_header.add_arcount(0)
    a_header.pack()
    
    print(a_header.get_data())
    out = a_header.unpack()
    print(bin(out[1]))