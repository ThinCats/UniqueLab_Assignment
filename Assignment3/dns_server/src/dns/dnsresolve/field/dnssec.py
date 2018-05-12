"""
This is for sections
Includes defination of RR
And question Sections
"""
import struct

if __package__:
    from . import codes
    from . import rdata
    from . import dnsname
else:
    import codes, rdata, dnsname

class Question(object):
    
    def __init__(self, a_name, a_type, a_class=codes.CLASS["IN"]):
        self._name = dnsname.DNSName.encode(a_name)
        self._type = a_type
        self._data = None
        self._class = a_class
        if not self._name:
            self._length = 1
        else:
            self._length = 0

    def get_name(self):
        return self._name
    def pack(self):
        self._data = struct.pack("!"+str(len(self._name))+"s"+"HH", self._name, self._type, self._class)
    
    @property
    def data(self):
        return self._data

    def __len__(self):
        return self._length

class RR(object):
    def __init__(self, a_name, a_type, a_ttl, a_class=codes.CLASS["IN"], a_rdata=None):
        self._name = dnsname.DNSName.encode(a_name)
        self._class = a_class

        self._type = a_type
        self._ttl = a_ttl

        if a_rdata:
            if not isinstance(a_rdata, rdata.RDATA):
                raise TypeError("[Err]a_rdata is not RDATA")
            else:
                self._rdata = a_rdata
                self._rdlength = len(a_rdata)
        else:
            self._rdata = None
            self._rdlength = None
        self._data = None

    def add_rdata_raw(self, a_data):
        if not isinstance(a_data, rdata.RDATA):
            raise TypeError("[Err]a_data is not RDATA")
        # TODO: Fullfill this
        self._rdata = a_data
        self._rdlength = len(a_data)
    
    def add_rdata(self, val):
        if self._type == codes.TYPE["A"]:
            self._rdata = rdata.A(val)
        if self._type == codes.TYPE["CNAME"]:
            self._rdata = rdata.CNAME(val)
        if self._type == codes.TYPE["NS"]:
            self._rdata = rdata.NS(val)
        
        self._rdlength = len(self._rdata)


    def pack(se
lf):
        if self._rdata == None:
            raise ValueError("[Err] rdata is empty")
        
        # From name to rdlength
        self._data = self._name
        self._data += struct.pack("!HHIH", self._type, self._class, self._ttl, self._rdlength)
        # pack rdata
        self._data += self._rdata.data
    
    @property
    def data(self):
        return self._data
    
    def __str__(self):
        return str(self._data)

class DNSSection(object):
    
    def __init__(self):
        self._RRlist = []
        self._data = b""
        self._rr_lens = 0

    
    def add_RR(self, a_RR):
        self._RRlist.append(a_RR)
        self._rr_lens += 1

    def pack(self):
        for a_RR in self._RRlist:
            a_RR.pack()
            self._data += a_RR.data

    @property
    def data(self):
        return self._data

    def __len__(self):
        return self._rr_lens
    def __str__(self):
        return str(self._data)


if __name__ == "__main__":
    # Question:
    que_res = Question(b"www.baidu.com", codes.TYPE["CNAME"])
    name = que_res.get_name()
    que_res.pack()
    print(que_res.data)
    # RR
    rr_test = RR("www.baidu.com", codes.TYPE["A"], 65535)
    rr_test.add_rdata("155.2.2.2")
    rr_test.pack()
    print(rr_test)

    rr_test_2 = RR("www.4399.com", codes.TYPE["CNAME"], 644, codes.CLASS["IN"], rdata.CNAME("www.hao123.com"))
    rr_test_2.pack()
    print(rr_test_2)
    # Sections
    section_test = DNSSection()
    for i in range(15): 
        section_test.add_RR(rr_test)
    section_test.add_RR(rr_test_2)

    section_test.pack()
    print(section_test)
    print(len(section_test))




