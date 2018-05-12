
import struct

if __package__:
    from .field import codes
    from . import dnsrecord
else:
    from field import codes
    import dnsrecord

def packet_to_record(raw_data):
    pass

def packet_split(raw_data):
    # First 12 bytes
    header = raw_data[:12]
    return (header, )
    



if __name__ == "__main__":

    raw_data = b"\x8e\xf7\x83\xb0\x00\x00\x00\x00\x00\x00\x00\x00\x044399\x03com\x00\x00\x01\x00\x01\x05baidu\x03com\x00\x00\x01\x00\x01\x00\x00\x02 \x00\x04{\x0c\x16\x16\x02gt\x03com\x00\x00\x02\x00\x01\x00\x00\x00{\x00\x0c\x03dns\x02ww\x03com\x00\x047k7k\x03com\x00\x00\x02\x00\x01\x00\x00\x00{\x00\x0f\x03dns\x05baidu\x03com\x00"
    packet_split(raw_data)