
"""
This defines the codes that will be used in resolver
"""

def reverse(a_dict):
    return dict([(val, key) for (key, val) in a_dict.items()])


VERSION = {
    "SOCKS5": 0x05,
}
VERSION_var = reverse(VERSION)

# This is for subnegotiation protocol
# Like user-password protocol
SUBVERSION = {
    "USERPASS": 0x01,
}
SUBVERSION_var = reverse(SUBVERSION)

METHOD = {
    "NONEED": 0x00,
    "GSSAPI": 0x01,
    "USERPASS": 0x02,
    "REFUSE": 0xFF
}
METHOD_var = reverse(METHOD)

ADDRESS = {
    "IPV4": 0x01,
    "DOMAIN": 0x03,
    "IPV6": 0x04
}
ADDRESS_var = reverse(ADDRESS)

REQUEST = {
    "CONNECT": 0x01,
    "BIND": 0x02,
    "UDP": 0x03
}
REQUEST_var = reverse(REQUEST)

STATUS = {
    "SUCCEED": 0x00,
    "SERVER": 0x01,
    "RULESET": 0x02,
    "NETWORK": 0x03,
    "HOST": 0x04,
    "CONNECTION": 0X05,
    "TTL": 0x06,
    "COMMAND": 0x07,
    "ADDRESS": 0x08,
}
STATUS_var = reverse(STATUS)


if __name__ == "__main__":
    print(STATUS_var[3])