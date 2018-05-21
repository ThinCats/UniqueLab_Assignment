
import struct
import socket

if __package__:
    from .field import codes, dnsname, bitsopr, dnsheader, dnssec
    from . import dnsrecord
else:
    from field import codes, dnsname, bitsopr, dnsheader, dnssec
    import dnsrecord
    
# For each request use DNSResolver to save data
# Then decode them (especially the name)
# Use dnsname's encode function
class DNSResolver(dnsname.DNSName):
    """
    vars are 
    _header
    _reused_lable
    
    """
    def __init__(self, data):
        """
        Must give the raw_data from client's response
        """
        # For saving map of pointer->lable
        self._reused_lable = {}
        if not type(data) == bytes:
            try:
                data = str(data)
            except TypeError:
                raise("[Err] Can't resolve the data")
        
        self._data = data
        self._record = dnsrecord.DNSRecord()
        self._count = None
        # For pointer
        self._offset = self.Offset()

        # 

    # FOR NAME RESOLVE
    # use recursive for recursive pointer

    # This class is for saving the offset
    # For dealing with RR sections
    class Offset(object):
        def __init__(self):
            self.ques = 12
            self.ans = 0
            self.auth = 0
            self.addi = 0
            
        
    def _decode_by_pointer(self, a_pointer):
        index = a_pointer
        lables = []
        while True:
            lable_len = self._data[index]
            if lable_len == 0:
                break
        # Pointer
        # Occur pointer means name ends
            elif bitsopr.get_bits(lable_len, 6, 7) == 3:
                pointer = bitsopr.get_bits(struct.unpack("!H", self._data[index:index+2])[0], 0, 13)
                # It means that it will exit later
                # So plus one to indicate the name last position
                index += 1
                val = self._reused_lable.get(pointer, None)
                if val:
                    lables += val
                    self._reused_lable[a_pointer] = lables
                    break
                else:
                    lables += self._decode_by_pointer(pointer)[0]
                    self._reused_lable[a_pointer] = lables
                    break
        # No
            else:
                index += 1
                lables.append(self._data[index:index+lable_len])
                index += lable_len
        return lables, index

    # Call _decode_by_pointer to handle pointer
    def _decode_by_name(self, a_name):
        index = 0
        lables = []
        while True:
            lable_len = a_name[index]
            if lable_len == 0:
                break
            elif bitsopr.get_bits(lable_len, 6, 7) == 3:
                pointer = bitsopr.get_bits(struct.unpack("!H", a_name[index:index+2])[0], 0, 13)
                lables += self._decode_by_pointer(pointer)[0]
                break
            else:
                index += 1
                lables.append(a_name[index:index+lable_len])
                index += lable_len
        
        return lables

    # There are only two condition when resolve with pointer
    # One is that whole lable is pointer, another is the end is pointer
    # And pointer will only exist once in each lable
    # Return the string for whole domain
    def decode_name(self, a_name):
        domain = b""
        lables = self._decode_by_name(a_name)
        for ch in lables:
            domain += (ch + b".")
        return str(domain, "ascii")

    def decode_name_raw(self, a_name):
        return self._decode_by_name(a_name)

    def decode_name_byoffset(self, offset):
        domain = b""
        lables, pointer = self._decode_by_pointer(offset)
        for ch in lables:
            domain += (ch + b".")
        return str(domain, "ascii"), pointer

    def decode_name_byoffset_raw(self, offset):
        return self._decode_by_pointer(offset)
    # FOR HEADER RESOLVE
    def unpack_header_raw(self, data=None):
        """
        Use self._data when pragm data is None
        """
        # Fixed byte size 12
        # TODO: automatically unpack
        if self._record._header:
            return self._record.header
        
        if not data == None:
            return struct.unpack("!12s", data[0:12])[0]
        else:
            header_data = struct.unpack("!12s", self._data[0:12])[0]
            self._record.add_header_raw(header_data, init=True)
            self._count = self._record.header.count
        
        return self._record._header

    def _rdata_resovle(self, rdata, a_type):
        # TODO Use another way
        # Rdata type: name
        type_name = codes.TYPE_val[a_type]
        if type_name in ["CNAME", "NS"]:
            return self.decode_name(rdata)
        # Rdata type: other:
        elif type_name == "A":
            return socket.inet_ntoa(rdata)
        elif type_name == "AAAA":
            return socket.inet_ntop(socket.AF_INET6,rdata)
    
    def unpack_question_raw(self, data=None):
        if data == None:
            # if unpacked
            if not self._record.question.is_empty():
                return self._record.question
            
            if not self._record.header:
                self.unpack_header_raw()
                self._count = self._record.header.count
            # Recursive iter the question
            index = self._offset.ques
            for i in range(self._count[0]):
                a_name, pointer = self.decode_name_byoffset(index)
                # Move to next position
                # self._record.add_que stion()
                pointer += 1
                a_type, a_class = struct.unpack("!HH", self._data[pointer:pointer+4])
                self._record.add_question(a_name, a_type, a_class)
                # Go where the pointer point
                # and then go Step 4 (type:2, class:2)
                index = pointer + 4            
            # Save in offset
            # print(index)
            self._offset.ans = index
        else:
            print("Unsupport")
        return self._record.question

    def unpack_answers_raw(self, data=None):
        """
        Use self._data when pram data is None
        """
        if data == None:
            # Recursive iter the answer:
            # Use ancount

            if not self._record.answer.is_empty():
                return self._record.answer
            
            # DEPENDECY ON QUESTION OFFSET
            if self._count ==None or self._offset.ans == 0:
                self.unpack_question_raw()


            index = self._offset.ans
            for i in range(self._count[1]):
                a_name, pointer = self.decode_name_byoffset(index)
                pointer += 1
                a_type, a_class, a_ttl, a_rdlength = struct.unpack("!HHIH", self._data[pointer:pointer+10])
                # Try uncompress name if rdata is names
                rdata = self._data[pointer+10:pointer+10+a_rdlength]
                rdata = self._rdata_resovle(rdata, a_type)

                self._record.add_answer(a_name, a_type, a_ttl, rdata, a_class=a_class)
                index = pointer + 10 + a_rdlength
                # print(index,codes.TYPE_val[a_type], rdata)
            self._offset.auth = index
        else:
            print("Temp does not support rawdata unpack -answers")

        return self._record.answer
                
    def unpack_auth_raw(self, data=None):
        """
        Use self._data when pram data is None
        Return record RR object
        """
        if data == None:
            # Recursive iter the answer:
            # Use ancount
            if not self._record.authority.is_empty():
                return self._record.authority
            # DEPENDECY ON QUESTION OFFSET
            if self._count == None or self._offset.auth == 0:
                self.unpack_answers_raw()


            index = self._offset.auth
            for i in range(self._count[2]):
                a_name, pointer = self.decode_name_byoffset(index)
                pointer += 1
                a_type, a_class, a_ttl, a_rdlength = struct.unpack("!HHIH", self._data[pointer:pointer+10])
                rdata = self._data[pointer+10:pointer+10+a_rdlength]
                # print(rdata)
                # Try uncompress name if rdata is names
                rdata = self._data[pointer+10:pointer+10+a_rdlength]
                rdata = self._rdata_resovle(rdata, a_type)
                self._record.add_auth(a_name, a_ttl, rdata, a_class=a_class)
                index = pointer + 10 + a_rdlength
                # print(index, a_name, a_ttl, codes.TYPE_val[a_type], rdata)
            self._offset.addi = index
        else:
            print("Temp does not support rawdata unpack -answers")
        return self._record.authority

    def unpack_addi_raw(self, data=None):
        """
        Use self._data when pram data is None
        """
        if data == None:
            # Recursive iter the addition:
            # Use ancount
            if not self._record.addition.is_empty():
                return self._record.addition
            # DEPENDECY ON QUESTION OFFSET
            if self._count == None or self._offset.addi == 0:
                self.unpack_auth_raw()


            index = self._offset.addi
            for i in range(self._count[3]):
                a_name, pointer = self.decode_name_byoffset(index)
                pointer += 1
                a_type, a_class, a_ttl, a_rdlength = struct.unpack("!HHIH", self._data[pointer:pointer+10])
                rdata = self._data[pointer+10:pointer+10+a_rdlength]
                # Try uncompress name if rdata is names
                rdata = self._data[pointer+10:pointer+10+a_rdlength]
                rdata = self._rdata_resovle(rdata, a_type)
                # print(rdata)
                self._record.add_addi(a_name, a_ttl, a_type, rdata)
                index = pointer + 10 + a_rdlength
                # print(index, a_name, a_ttl, codes.TYPE_val[a_type], rdata)
            # self._offset.addi = index
        else:
            print("Temp does not support rawdata unpack -answers")      

    def unpack_all(self):
        self.unpack_header_raw()
        self.unpack_question_raw()
        self.unpack_answers_raw()
        self.unpack_auth_raw()
        self.unpack_addi_raw()
        return self._record
    
    def pack_just_header(self):
        """
        This is for recursive query
        and for cache saving
        just pack header and other use remaining data
        RETURN DATA
        """
        if not self._record.header:
            raise TypeError("[Err] record.header does not exist")
        # PACK
        self.record._header.pack()
        return self.record._header.data + self._data[12:]


        
    @property
    def record(self):
        return self._record

    @property
    def packed_data(self):
        return self._record._data
    





if __name__ == "__main__":


    raw_data =  b"\x15\x0d\x81\x80\x00\x01\x00\x02\x00\x05\x00\x05\x02\x68\x6d\x05" \
b"\x62\x61\x69\x64\x75\x03\x63\x6f\x6d\x00\x00\x01\x00\x01\xc0\x0c" \
b"\x00\x05\x00\x01\x00\x00\x0f\xed\x00\x0e\x02\x68\x6d\x01\x65\x06" \
b"\x73\x68\x69\x66\x65\x6e\xc0\x15\xc0\x2a\x00\x01\x00\x01\x00\x00" \
b"\x00\xb1\x00\x04\xca\x6c\x17\x98\xc0\x2d\x00\x02\x00\x01\x00\x01" \
b"\x45\x4d\x00\x06\x03\x6e\x73\x33\xc0\x2d\xc0\x2d\x00\x02\x00\x01" \
b"\x00\x01\x45\x4d\x00\x06\x03\x6e\x73\x34\xc0\x2d\xc0\x2d\x00\x02" \
b"\x00\x01\x00\x01\x45\x4d\x00\x06\x03\x6e\x73\x32\xc0\x2d\xc0\x2d" \
b"\x00\x02\x00\x01\x00\x01\x45\x4d\x00\x06\x03\x6e\x73\x31\xc0\x2d" \
b"\xc0\x2d\x00\x02\x00\x01\x00\x01\x45\x4d\x00\x06\x03\x6e\x73\x35" \
b"\xc0\x2d\xc0\x8a\x00\x01\x00\x01\x00\x00\x01\xeb\x00\x04\x3d\x87" \
b"\xa5\xe1\xc0\x78\x00\x01\x00\x01\x00\x00\x01\xeb\x00\x04\xb4\x95" \
b"\x85\xf2\xc0\x54\x00\x01\x00\x01\x00\x00\x01\xeb\x00\x04\x3d\x87" \
b"\xa2\xd9\xc0\x66\x00\x01\x00\x01\x00\x00\x01\xeb\x00\x04\x73\xef" \
b"\xd2\xb1\xc0\x9c\x00\x01\x00\x01\x00\x00\x01\xeb\x00\x04\x77\x4b" \
b"\xde\x0d"



    res = DNSResolver(raw_data)
    name = b"\xc0\x0c\x00\x05\x00\x01\x00\x00\x08\x5e\x00\x2d\x06\x61\x73\x69" \
b"\x6d\x6f\x76\x06\x76\x6f\x72\x74\x65\x78\x04\x64\x61\x74\x61\x09" \
b"\x6d\x69\x63\x72\x6f\x73\x6f\x66\x74\x03\x63\x6f\x6d\x06\x61\x6b" \
b"\x61\x64\x6e\x73\x03\x6e\x65\x74\x00\xc0\x37\x00\x05\x00\x01\x00" \
b"\x00\x01\x04\x00\x06\x03\x67\x65\x6f\xc0\x3e\xc0\x70\x00\x05\x00" \
b"\x01\x00\x00\x00\x74\x00\x06\x03\x68\x6b\x32\xc0\x3e"

    # print(raw_data.find(name))
    print(len(raw_data))
    # print(res.decode_name(name))
    # print(res.decode_name_raw(name))

    # print(res.decode_name_byoffset(43))
    # print(res.unpack_header_raw())
    res.unpack_answers_raw()
    # res.unpack_question_raw()
    # res.unpack_auth_raw()
    res.unpack_addi_raw()
    print(res.pack_just_header())

    