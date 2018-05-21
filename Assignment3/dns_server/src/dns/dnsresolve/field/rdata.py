"""
This is Rdata for RR
"""

import struct
import logging
import socket
logger = logging

if __package__:
    from . import dnsname
else:
    import dnsname



class RDATA(object):
    """
    For each RDATA
    __str__ return their value
    like A: 192.1.1.1
    like CNAME: baidu.com

    _data save the raw binary
    """
    def __init__(self):
        self._data = None
        self._val = None
    
    @property
    def data(self):
        return self._data
    @property
    def val(self):
        return self._val
    
    def __len__(self):
        return len(self._val)
    
    def __str__(self):
        return str(self._val)

class NotSupportRDATA(RDATA):
    
    @classmethod
    def error(cls):
        logger.debug("Found  type, but we temporily not suppor, sorry for that")

    def pack(self):
        self._data = b""
        return 
    def __init__(self, val):

        NotSupportRDATA.error()
        self._val = val
        self._data = b""


class A(RDATA):

    def ori_pack(self):
        ip_addr = self._val
        lables = ip_addr.split(".")
        out = []
        for lable in lables:
            out.append(int(lable))
        self._data =  struct.pack("!BBBB", out[0], out[1], out[2], out[3])
    
    def pack(self):
        self._data = socket.inet_aton(self._val)
    def __init__(self, ip_addr):
        self._ip = ip_addr
        self._val = ip_addr
        # Pack at once
        self._data = None
        self.pack()
        # self._data = A.pack(ip_addr)

    @property
    def ip(self):
        return self._ip

class AAAA(RDATA):

    def pack(self):
        self._data = socket.inet_pton(socket.AF_INET6, self._val)
    
    def __init__(self, val):
        self._val = val
        self._data = None
        self.pack()


class CNAME(RDATA):

    def pack(self):
        # Use no compress
        self._data = dnsname.DNSName.encode(self._val)
    
    def __init__(self, a_domain):
        # self._data = dnsname.DNSName.encode(a_domain)
        self._domain = a_domain
        self._val = a_domain
        # Pack for rdlength
        self._data = None
        self.pack()

    @property
    def domain(self):
        return self._domain
    
class NS(CNAME):
    """
    The packed data is same as CNAME
    """
    pass

class OPT(NotSupportRDATA):
    """
    This is for extra
    """
    pass
    

class SOA(NotSupportRDATA):
    pass

rdataClassList = {
    "AAAA":AAAA,
    "A":A,
    "CNAME":CNAME,
    "NS":NS,
    "OPT":OPT,

}
if __name__ == "__main__":
    a_rec = A("1.1.1.1")
    print(len(a_rec))

    cname = CNAME("www.baidu.com")
    cname.pack()
    print(cname)
    print(cname.data)

