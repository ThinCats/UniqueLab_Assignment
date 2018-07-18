import struct
import socket

if __package__:
    from . import codes
else:
    import codes

two_B_struct = struct.Struct(">BB")
def srv_decode(data_raw):

    frag, addr_type = two_B_struct.unpack_from(data_raw[:4], 2)

    addr = ""
    port = 0
    data_user = b""
    # Now only support ipv4
    if addr_type == codes.ADDRESS["IPV4"]:
        # 4 bits of the address
        addr = socket.inet_ntoa(data_raw[4:8])
        port, = struct.unpack_from(">H", data_raw[:10], 8)
        data_user = data_raw[10:]
    
    elif addr_type == codes.ADDRESS["IPV6"]:
        pass
    elif addr_type == codes.ADDRESS["DOMAIN"]:
        pass
    else:
        raise TypeError("Not support address type {}".format(addr_type))
    
    return (frag, addr_type, (addr, port), data_user)

def srv_encode(frag, addr_type, addr, port, data_user):
    if not type(data_user) is bytes:
        raise TypeError("Data_user is not Bytes!")
    
    out = b""
    # Now only support ipv4
    if addr_type == codes.ADDRESS["IPV4"]:
        # 4 bits of the address
        out = socket.inet_aton(addr) + struct.pack(">H", port)

    elif addr_type == codes.ADDRESS["IPV6"]:
        pass
    elif addr_type == codes.ADDRESS["DOMAIN"]:
        pass
    else:
        raise TypeError("No support address type {}".format(addr_type))
    
    return b"\x00\x00" + two_B_struct.pack(frag, addr_type) + out + data_user

def cli_encode(frag, addr_type, addr, port, data_user):
    return srv_encode(frag, addr_type, addr, port, data_user)

def cli_decode(data_raw):
    return srv_decode(data_raw)

if __name__ == "__main__":
    a = srv_encode(12, 1, "113.113.4.2", 80, b"123wqeq12")
    print(a)
    print(srv_decode(a))