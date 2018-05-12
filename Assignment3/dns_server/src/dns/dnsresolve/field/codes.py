import struct
__all__ = ["reverse"]
"""
This includes basic bit-codes that will be used in Header
Or use as Class and Type

For Example:
QR, AA, TC...
IN...
CNAME...

Use Dict and Normal var to set
I know it's seemed a little funny
TODO: Use Other data structure
"""

# For reversing the Dict for map num->field_name
def reverse(a_dict):
    return dict([(val, key) for (key, val) in a_dict.items()])

# header

# QR
QR = {"query":0, "response":1}
QR_val = reverse(QR)

# OPCODE
OPCODE = {"query":0x00, "notify":0x04, "update":0x05}
OPCODE_var = reverse(OPCODE)

# FLAG

# RCODE
# Refer to TCP/IP Illustrated P370
RCODE = ({"NoError":0, "FormErr":1, "ServErr":2, "NXDomain":3, "NotImp":4, "Refused":5, "YXDomain":6, "YXRRSet":7, 
"NXRRSet":8, "NotAuth":9, "NotZone":10})
RCODE_val = reverse(RCODE)

# TYPE
# used for query type
TYPE = ({"A":1, "NS":2, "CNAME":5, "SOA":6, "PTR":12, "MX":15, "TXT":16, "AAAA":28, "SRV":33, "NAPTR":35, "OPT":41, 
"IXFR":251, "AXFR":252, "ANY":255})
TYPE_val = reverse(TYPE)

# CLASS
CLASS = {"IN":1, "None":254, "*":255}
CLASS_val = reverse(CLASS)


if __name__ == "__main__":
    print(TYPE["CNAME"])