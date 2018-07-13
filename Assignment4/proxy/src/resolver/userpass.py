
import struct

if __package__:
    from . import codes
else:
    import codes

two_B_struct = struct.Struct(">2B")
def srv_encode(status, version=codes.SUBVERSION["USERPASS"]):
    return two_B_struct.pack(version, status)

def cli_decode(data_raw):
    return two_B_struct.unpack(data_raw)

def cli_encode(username, password, version=codes.SUBVERSION["USERPASS"]):
    return two_B_struct.pack(version, len(username)) + bytes(username, "ascii") + struct.pack(">B", len(password)) + bytes(password, "ascii")

def srv_decode(data_raw):
    version, len_user = two_B_struct.unpack(data_raw[:2])
    username = str(data_raw[2:2+len_user], "ascii")
    len_pass, = struct.unpack(">B", data_raw[2+len_user:3+len_user])
    password = str(data_raw[3+len_user:3+len_user+len_pass], "ascii")
    return (version, username, password)

if __name__ == "__main__":
    raw  = cli_encode( "Brody", "1234d")
    print(raw)
    print(cli_decode(raw))