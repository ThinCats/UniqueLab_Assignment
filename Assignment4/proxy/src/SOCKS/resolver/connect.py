import struct
import socket

if __package__:
    from . import codes
else:
    import codes

"""
This is the second process
Handle the connection request
"""

four_B_struct = struct.Struct(">BBBB")

def srv_decode(data_raw):
    ver, request, rever, addr_type = four_B_struct.unpack(data_raw[:4])
    addr = ""
    port = 0
    # Now only support ipv4
    if addr_type == codes.ADDRESS["IPV4"]:
        # 4 bits of the address
        addr = socket.inet_ntoa(data_raw[4:8])
        port, = struct.unpack_from(">H", data_raw, 8)

    elif addr_type == codes.ADDRESS["IPV6"]:
        pass
    elif addr_type == codes.ADDRESS["DOMAIN"]:
        addr_len, = struct.unpack(">B", data_raw[4:5])
        addr = str(struct.unpack(">"+str(addr_len)+"s", data_raw[5:5+addr_len])[0], "ascii")
        port, = struct.unpack_from(">H", data_raw, 5+addr_len)
    else:
        raise TypeError("No support address type {}".format(addr_type))
    
    return (ver, request, addr_type, (addr, port))

def srv_encode(status, addr_type, addr, port, version=codes.VERSION["SOCKS5"]):
    out = b""
    # Now only support ipv4
    if addr_type == codes.ADDRESS["IPV4"]:
        # 4 bits of the address
        out = socket.inet_aton(addr) + struct.pack(">H", port)

    elif addr_type == codes.ADDRESS["IPV6"]:
        pass
    elif addr_type == codes.ADDRESS["DOMAIN"]:
        out = struct.pack(">B", len(addr)) + bytes(addr, "ascii") + struct.pack(">H", port)
    else:
        raise TypeError("No support address type {}".format(addr_type))
    
    return four_B_struct.pack(version, status, 0, addr_type) + out

def cli_decode(data_raw):
    return srv_decode(data_raw)

def cli_encode(request_type, addr_type, addr, port, version=codes.VERSION["SOCKS5"]):
    return srv_encode(request_type, addr_type, addr, port, version)

if __name__ == "__main__":
    a = srv_encode(0, 1, "1.1.1.1", 50)
    print(a)
    print(srv_decode(a))
    b = srv_encode(0, codes.ADDRESS["DOMAIN"], "baidu.com.", 80)
    print(b)
    print(srv_decode(b))