"""
This is Rdata for RR
"""

import struct

import codes
import dnsname


class RDATA(object):

    def __init__(self):
        self._data = None
    
    @property
    def data(self):
        return self._data

    def __len__(self):
        return len(self._data)
    
    def __str__(self):
        return str(self._data)

class A(RDATA):

    @classmethod
    def pack(cls, ip_addr):
        lables = ip_addr.split(".")
        out = []
        for lable in lables:
            out.append(int(lable))
        return struct.pack("!BBBB", out[0], out[1], out[2], out[3])
    def __init__(self, ip_addr):
        self._data = A.pack(ip_addr)


class CNAME(RDATA):

    def __init__(self, a_domain):
        self._data = dnsname.DNSName.encode(a_domain)
    
class NS(RDATA):

    def __init__(self, a_domain):
        self._data = dnsname.DNSName.encode(a_domain)


if __name__ == "__main__":
    a_rec = A("1.1.1.1")
    print(a_rec.data)
    print(len(a_rec.data))
    print(len(a_rec))

    cname = CNAME("www.baidu.com")
    print(cname)


