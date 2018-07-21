
import struct

if __package__:
    from . import codes
else:
    import codes

  # Request
  # VERSION | REQUEST | PORT
  # Response
  # VERSION | STATUS | PORT

BBH_struct = struct.Struct(">BBH")
def cli_encode(version, request, port):
    return BBH_struct.pack(version, request, port)

def cli_decode(data_raw):
    return BBH_struct.unpack(data_raw)

def srv_encode(version, status, port):
    return BBH_struct.pack(version, status, port)

def srv_decode(data_raw):
    return BBH_struct.unpack(data_raw)

if __name__ == "__main__":

    a = cli_encode(codes.VERSION["V1"], codes.REQUEST["FORWARD"], 80)
    print(a)
    print(srv_decode(a))