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
        self._name_val = a_name
        self._type = a_type
        self._data = None
        self._class = a_class
        if not self._name:
            self._length = 1
        else:
            self._length = 0

    @property
    def unpacked_data(self):
        """
        data unpacked
        return tuple(name, type, class)
        """
        return (self._name_val, self._type, self._class)
    @property
    def name(self):
        return self._name_val
    
    @property
    def type_str(self):
        return codes.TYPE_val[self._type]
    @property
    def qtype(self):
        return self._type
    def pack(self):
        self._data = struct.pack("!"+str(len(self._name))+"s"+"HH", self._name, self._type, self._class)
    
    @property
    def data(self):
        return self._data

    def __len__(self):
        return self._length

    def __str__(self):
        return (str(self._name_val) + ' ' + codes.TYPE_val[self._type] + ' ' +  codes.CLASS_val[self._class])

class RR(object):
    def __init__(self, a_name, a_type, a_ttl, a_class=codes.CLASS["IN"], a_rdata=None):
        self._name = dnsname.DNSName.encode(a_name)
        self._name_val = a_name
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

    def _add_rdata_raw_bytes(self, a_data):
        
        # TODO: Fullfill this
        self._rdata = a_data
        self._rdlength = len(a_data)
    
    def add_rdata(self, val):
        if type(val) == bytes:
            self._add_rdata_raw_bytes(val)
            return

        try:
            self._rdata = rdata.rdataClassList[codes.TYPE_val[self._type]](val)
        except KeyError:
            raise KeyError("add rdata wrong type")
        
        self._rdlength = len(self._rdata.data)


    def pack(self):
        if self._rdata == None:
            raise ValueError("[Err] rdata is empty")
        
        # From name to rdlength
        self._data = self._name
        self._data += struct.pack("!HHIH", self._type, self._class, self._ttl, self._rdlength)
        # pack rdata
        if not self._rdata.data:
            self._rdata.pack()
        self._data += self._rdata.data
    
    @property
    def data(self):
        return self._data
    @property
    def name(self):
        return self._name_val
    @property
    def qtype(self):
        return self._type
    @property
    def ttl(self):
        return self._ttl
    
    @property
    def unpacked_data(self):
        """
        Return tuple(name, type, class, ttl, rdlength, rdata)
        Rdata is name or ip with string
        """
        return (self._name_val, self._type, self._class, self._ttl, self._rdlength, self._rdata.val)
    def __str__(self):
        return (str(self._name_val) + ' ' + str(codes.TYPE_val[self._type]) + ' ' + codes.CLASS_val[self._class] + ' ' + str(self._ttl) + ' ' + str(self._rdlength) + ' ' + str(self._rdata)) 


class DNSSection(object):
    """
    For both RR object and question
    A wrapper list
    """
    def __init__(self):
        self._RRlist = []
        self._data = b""
        self._rr_lens = 0

    
    def add_RR(self, a_RR):
        """
        RR can also judge as question
        """
        self._RRlist.append(a_RR)
        self._rr_lens += 1
    def append(self, a_RR):
        self.add_RR(a_RR)
    
    def pack(self):
        for a_RR in self._RRlist:
            a_RR.pack()
            self._data += a_RR.data
        return self._data

    @property
    def data(self):
        return self._data
    @property
    def rrlist(self):
        return self._RRlist
    
    def is_empty(self):
        """
        Judge whether contains elements
        """
        return self._rr_lens == 0
    
    def __len__(self):
        return self._rr_lens
    def __str__(self):
        return str([str(x) for x in self._RRlist])


if __name__ == "__main__":
    # Question:
    que_res = Question(b"www.baidu.com", codes.TYPE["CNAME"])
    name = que_res.name
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




