
if __package__:
    from .field import dnsheader
    from .field import dnssec
    from .field import codes   
    from .field import dnsflag 
else:
    from field import dnsheader
    from field import dnssec
    from field import codes
    from field import dnsflag


class DNSRecord(object):

    def __init__(self, bheader=None, bques=None, bans=None, bauth=None, baddi=None):
        # pragms are raw bin data

        self._header = None
        self._ques = dnssec.DNSSection()
        self._ans = dnssec.DNSSection()
        self._auth = dnssec.DNSSection()
        self._addi = dnssec.DNSSection()
        
        # Packed data:
        # For raw opr functions
        self._header_pack = bheader
        self._ques_pack = bques
        self._ans_pack = bans
        self._auth_pack = bauth
        self._addi_pack = baddi

        self._data = b""
    
    def add_header_raw(self, header_raw, init=False):
        if not type(header_raw) == bytes:
            raise TypeError("[Err]header_raw is not bytes")
        self._header_pack = header_raw

        # To create a class not just header_raw_data
        if init:
            self._header = dnsheader.DNSHeader(header_raw_data=header_raw)
    
    def add_header_class(self, a_header):
        self._header = a_header
    def add_header(self, qr, opcode, aa, tc, rd, ra, ad, rcode, z=0, cd=1, id=None):
        self._header = dnsheader.DNSHeader()
        self._header.add_id(id)
        self._header.add_flag(qr, opcode, aa, tc, rd, ra, ad, rcode, z, cd)

    # Modify the header existing in DNSRecord
    # support both for raw data and class data
    def modify_header(self, **kw):
        """
        Only change what will change
        Remain other fields
        """
        # Trans raw data to class
        # Convenient for updating length
        if self._header_pack:
            self._header = dnsheader.DNSHeader.unpack_class(self._header_pack)
            self._header_pack = None
        self._header.modify_flag(**kw)
        self._header.modify_id(kw.get("id", self._header.id))


    # Read from header as item
    def read_header_one(self, item):
        """
        item means qr aa id something
        """
        if item == "id":
            return self._header.id
        elif item == "count":
            return self._header.count
        elif item in ("qr", "opcode", "aa", "tc", "rd", "ra", "z", "ad", "cd", "rcode"):
            return self._header.read_flag(self, item)
        else:
            raise ValueError("[Err] Can't read %s from header" %(item))

    def read_header_full(self):
        """
        read header means
        return a list contains every field
        """
        out = []
        out.append(self._header.id)
        # Read the field:
        for item in ("qr", "opcode", "aa", "tc", "rd", "ra", "z", "ad", "cd", "rcode"):
            out.append(self._header.read_flag(item))
        return out
        
    # TODO: automatically update
    def update_header(self):
        self._header.add_ancount(len(self._ans))
        self._header.add_qdcount(len(self._ques))
        self._header.add_nscount(len(self._auth))
        self._header.add_arcount(len(self._addi))

    # _class means it's the format of Questions
    # Questions{}
    def add_question_class(self, ques):
        if not isinstance(ques, dnssec.Questions):
            raise TypeError("[Err] ques is not Question")
        self._ques.append(ques)
    
    # _raw means it's the packed data
    # b""
    def add_question_raw(self, ques_raw):
        self._ques_pack = ques_raw

    def add_question(self, a_name, a_type, a_class=codes.CLASS["IN"]):
        self._ques.add_RR(dnssec.Question(a_name, a_type, a_class))
        return True
    
    def add_answer_class(self, ans):
        if not isinstance(ans, dnssec.DNSSection):
            raise TypeError("[Err] ans is not Answer")
        self._ans.add_RR(ans)

    def add_answer_raw(self, ans_raw):
        if not isinstance(ans_raw, bytes):
            raise TypeError("[Err] ans_raw is not bytes")
        self._ans_pack = ans_raw
    
    def add_answer(self, a_name, a_type, a_ttl, rdata_val, a_class=codes.CLASS["IN"]):
        rr_item = dnssec.RR(a_name, a_type, a_ttl, a_class)
        rr_item.add_rdata(rdata_val)
        self._ans.add_RR(rr_item)

    def add_auth_raw(self, auth_raw):
        if not isinstance(auth_raw, bytes):
            raise TypeError("[Err] auth_raw is not bytes")
        self._auth_pack = auth_raw
    
    def add_auth(self, a_name, a_ttl, rdata_val, a_type=codes.TYPE["NS"], a_class=codes.CLASS["IN"]):
        rr_item = dnssec.RR(a_name, a_type, a_ttl, a_class)
        rr_item.add_rdata(rdata_val)
        self._auth.add_RR(rr_item)

    def add_addi_raw(self, addi_raw):
        if not isinstance(addi_raw, bytes):
            raise TypeError("[Err] addi_raw is not bytes")
        self._addi_pack = addi_raw
    
    def add_addi(self, a_name, a_ttl, a_type, rdata_val, a_class=codes.CLASS["IN"]):
        rr_item = dnssec.RR(a_name, a_type, a_ttl)
        rr_item.add_rdata(rdata_val)
        self._addi.add_RR(rr_item)
    
    def pack(self):
        # self.update_header()
        # self._header.pack()
        # self._data += self._header.data
        # self._data += self.list_pack(self._ques) + self.list_pack(self._ans) + self.list_pack(self._auth) + self.list_pack(self._addi)

        # For raw data appending
        if self._header_pack:
            self._data += self._header_pack
        else:
            self.update_header()
            self._header.pack()
            self._data += self._header.data
        if self._ques_pack:
            self._data += self._ques_pack
        else:
            self._data += self._ques.pack()
        if self._ans_pack:
            self._data += self._ans_pack
        else:
            self._data += self._ans.pack()
        if self._auth_pack:
            self._data += self._auth_pack
        else:
            self._data += self._auth.pack()
        if self._addi_pack:
            self._data += self._addi_pack
        else:
            self._data += self._addi.pack()


    @property
    def data(self):
        return self._data
    @property 
    def header(self):
        return self._header
    @property
    def question(self):
        return self._ques
    @property
    def answer(self):
        return self._ans
    @property
    def authority(self):
        return self._auth
    @property
    def addition(self):
        return self._addi

    def __len__(self):
        return len(self._data)

    def __str__(self):
        return str(self._data)
        

        



if __name__ == "__main__":
    record = DNSRecord()
    record.add_header(0, codes.OPCODE["query"],0, 1, 1, 1, 1, codes.RCODE["NoError"])

    record.add_answer("baidu.com", codes.TYPE["A"], 544, "123.12.22.22")
    record.add_question("4399.com", codes.TYPE["A"])
    record.add_addi("7k7k.com", 123, codes.TYPE["NS"], "dns.baidu.com")
    record.add_auth("gt.com", 123, "dns.ww.com")
    # record.pack()

    print(record.answer.is_empty())
    print(record.answer)
    # print(record)
    record = DNSRecord()
    record.add_header_raw(b"\x8e\xf7\x03\xb0\x00\x01\x00\x01\x00\x01\x00\x01")
    record.add_question_raw(b"\x044399\x03com\x00\x00\x01\x00\x01")
    record.add_answer_raw(b"\x05baidu\x03com\x00\x00\x01\x00\x01\x00\x00\x02 \x00\x04{\x0c\x16\x16")
    record.add_auth_raw(b"\x02gt\x03com\x00\x00\x02\x00\x01\x00\x00\x00{\x00\x0c\x03dns\x02ww\x03com\x00")
    record.add_addi_raw(b"\x047k7k\x03com\x00\x00\x02\x00\x01\x00\x00\x00{\x00\x0f\x03dns\x05baidu\x03com\x00")
    # record.pack()
    print(record)
    record.modify_header(qr=1)
    record.pack()
    print(record)


