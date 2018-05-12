
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

        self._header = dnsheader.DNSHeader()
        self._ques = []
        self._ans = []
        self._auth = []
        self._addi = []
        
        # Packed data:
        # For raw opr functions
        self._header_pack = bheader
        self._ques_pack = bques
        self._ans_pack = bans
        self._auth_pack = bauth
        self._addi_pack = baddi

        self._data = b""
    
    def add_header_raw(self, header_raw):
        if not type(header_raw) == bytes:
            raise TypeError("[Err]header_raw is not bytes")
        self._header_pack = header_raw
    
    def add_header(self, qr, opcode, aa, tc, rd, ra, ad, rcode, z=0, cd=1, id=None):
        self._header.add_id(id)
        self._header.add_flag(qr, opcode, aa, tc, rd, ra, ad, rcode, z, cd)
    
    # Modify the header existing in DNSRecord
    # support both for raw data and class data
    def modify_header(self, **kw):

        # Trans raw data to class
        # Convenient for updating length
        if self._header_pack:
            self._header = dnsheader.DNSHeader.unpack(self._header_pack)
            self._header_pack = None
        self._header.modify_flag(**kw)
        self._header.modify_id(kw.get("id", self._header.id))

        print(self._header.flag, self._header.id)

    # Read from header as item
    def read_header(self, item):
        if item == "id":
            return self._header.id
        elif item == "count":
            return self._header.count
        elif item in ("qr", "opcode", "aa", "tc", "rd", "ra", "z", "ad", "cd", "rcode"):
            return self._header.read_flag(self, item)
        else:
            raise ValueError("[Err] Can't read %s from header" %(item))

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
        self._ques.append(dnssec.Question(a_name, a_type, a_class))
        return True
    
    def add_answer_class(self, ans):
        if not isinstance(ans, dnssec.DNSSection):
            raise TypeError("[Err] ans is not Answer")
        self._ans.append(ans)

    def add_answer_raw(self, ans_raw):
        if not isinstance(ans_raw, bytes):
            raise TypeError("[Err] ans_raw is not bytes")
        self._ans_pack = ans_raw
    
    def add_answer(self, a_name, a_type, a_ttl, rdata_val, a_class=codes.CLASS["IN"]):
        rr_item = dnssec.RR(a_name, a_type, a_ttl, a_class)
        rr_item.add_rdata(rdata_val)
        ans_item = dnssec.DNSSection()
        ans_item.add_RR(rr_item)
        self._ans.append(ans_item)

    def add_auth_raw(self, auth_raw):
        if not isinstance(auth_raw, bytes):
            raise TypeError("[Err] auth_raw is not bytes")
        self._auth_pack = auth_raw
    
    def add_auth(self, a_name, a_ttl, rdata_val, a_type=codes.TYPE["NS"], a_class=codes.CLASS["IN"]):
        rr_item = dnssec.RR(a_name, a_type, a_ttl, a_class)
        rr_item.add_rdata(rdata_val)
        auth_item = dnssec.DNSSection()
        auth_item.add_RR(rr_item)
        self._auth.append(auth_item)

    def add_addi_raw(self, addi_raw):
        if not isinstance(addi_raw, bytes):
            raise TypeError("[Err] addi_raw is not bytes")
        self._addi_pack = addi_raw
    
    def add_addi(self, a_name, a_ttl, a_type, rdata_val, a_class=codes.CLASS["IN"]):
        rr_item = dnssec.RR(a_name, a_type, a_ttl)
        rr_item.add_rdata(rdata_val)
        addi_item = dnssec.DNSSection()
        addi_item.add_RR(rr_item)
        self._addi.append(addi_item)
    
    @staticmethod
    def list_pack(a_list):
        a_out = b""
        for i in a_list:
            i.pack()
            a_out += i.data
        return a_out
    
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
            self._data += self.list_pack(self._ques)
        if self._ans_pack:
            self._data += self._ans_pack
        else:
            self._data += self.list_pack(self._ans)
        if self._auth_pack:
            self._data += self._auth_pack
        else:
            self._data += self.list_pack(self._auth)
        if self._addi_pack:
            self._data += self._addi_pack
        else:
            self._data += self.list_pack(self._addi)

        

    @property
    def data(self):
        return self._data
    
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


