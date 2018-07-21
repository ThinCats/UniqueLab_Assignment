import struct

H_struct = struct.Struct(">H")
def decode_cli(data_raw):
    return H_struct.unpack(data_raw)[0]

def encode_srv(port):
    return H_struct.pack(port)
