import struct
import random

if not __package__:
    import codes
else:
    from . import codes

BH_struct = struct.Struct(">BH")
def cli_encode():
    return codes.magic_str.encode("ascii")

def srv_encode(is_verified):
    ran_num = random.randint(*codes.random_range)
    ver_num = (codes.VERIFY["YES"] if (is_verified) else codes.VERIFY["NO"])
    data_raw = BH_struct.pack(ver_num, ran_num) + codes.magic_str.encode("ascii")
    return (data_raw, ran_num)

def cli_decode(data_raw):
    return BH_struct.unpack(data_raw[:len(data_raw)-len(codes.magic_str)])

def srv_decode(data_raw):
    return data_raw


if __name__ == "__main__":
    a = srv_encode(True)
    print(a)
    print(cli_decode(a))