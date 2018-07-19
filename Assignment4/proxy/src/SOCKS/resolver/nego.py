import struct

if __package__:
    from . import codes

else:
    import codes

# This is first process for negotiation
"""
Naming Rules:
  1. Method
    cli_encode() means:
    1. cli: The method is for client use
    2. encode: The method is for encoding data to bytes
  
  2. Local varibales
    data_raw means bytes
    data means decoded data
"""

# This is for accelerating struct pack speed
two_B_struct = struct.Struct(">BB")

def srv_decode(data_raw):
    ver, nums_method = two_B_struct.unpack(data_raw[:2])
    methods = struct.unpack_from(">" + str(nums_method)+"B", data_raw, 2)

    return (ver, methods)

def srv_encode(method, version=codes.VERSION["SOCKS5"]):
    return two_B_struct.pack(version, method)

def cli_decode(data_raw):
    return two_B_struct.unpack(data_raw)

def cli_encode(methods, version=codes.VERSION["SOCKS5"]):
    if type(methods) is int:
        methods = (methods, )
    return two_B_struct.pack(version, len(methods)) + struct.pack(">"+str(len(methods))+"B", *methods)

if __name__ == "__main__":
    print(srv_decode(b"\x01\x02\x03\x04"))
    print(srv_encode(codes.METHOD["NONEED"]))
    print(cli_encode((3, 4, 6)))
