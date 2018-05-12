"""
For gen flags
"""

if __package__:
    from . import codes
    from . import dnsflag
    from .bitsopr import set_bits, get_bits, print_bits
else:
    import codes, dnsflag
    from bitsopr import set_bits, get_bits, print_bits


def set_qr(a_flag, qr):
    return set_bits(a_flag, qr, 15, 15)

def get_qr(a_flag):
    return get_bits(a_flag, 15, 15)

def set_opcode(a_flag, opcode):
    return set_bits(a_flag, opcode, 11, 14)

def get_opcode(a_flag):
    return get_bits(a_flag, 11, 14)

def set_rcode(a_flag, rcode):
    return set_bits(a_flag, rcode, 0, 3)

def get_rcode(a_flag):
    return get_bits(a_flag, 0, 3)

def set_aa(a_flag, aa):
    return set_bits(a_flag, aa, 10, 10)
def get_aa(a_flag):
    return get_bits(a_flag, 10, 10)

def set_tc(a_flag, tc):
    return set_bits(a_flag, tc, 9, 9)
def get_tc(a_flag):
    return get_bits(a_flag, 9, 9)

def set_rd(a_flag, rd):
    return set_bits(a_flag, rd, 8, 8)
def get_rd(a_flag):
    return get_bits(a_flag, 8, 8)

def set_ra(a_flag, ra):
    return set_bits(a_flag, ra, 7, 7)
def get_ra(a_flag):
    return get_bits(a_flag, 7, 7)

def set_z(a_flag, z):
    return set_bits(a_flag, z, 6, 6)
def get_z(a_flag):
    return get_bits(a_flag, 6, 6)

def set_ad(a_flag, ad):
    return set_bits(a_flag, ad, 5, 5)
def get_ad(a_flag):
    return get_bits(a_flag, 5, 5)

def set_cd(a_flag, cd):
    return set_bits(a_flag, cd, 4, 4)
def get_cd(a_flag):
    return get_bits(a_flag, 4, 4)

def pack_flag(flag, qr, opcode, aa, tc, rd, ra, ad, rcode, cd=1, z=0):
    flag = set_qr(flag, qr)
    flag = set_opcode(flag, opcode)
    flag = set_aa(flag, aa)
    flag = set_tc(flag, tc)
    flag = set_rd(flag, rd)
    flag = set_ra(flag, ra)
    flag = set_ad(flag, ad)
    flag = set_rcode(flag, rcode)
    flag = set_z(flag, z)
    flag = set_cd(flag, cd)
    return flag

def unpack_flag(flag):
    result = []
    pass

# functions Dict for **kw
setFunctions = {
    "qr":set_qr,
    "aa":set_aa,
    "ad":set_ad,
    "rcode":set_rcode,
    "opcode":set_opcode,
    "tc":set_tc,
    "z":set_z,
    "cd":set_cd,
    "rd":set_rd,
    "ra":set_ra,
}

getFunctions = {
    "qr":get_qr,
    "aa":get_aa,
    "ad":get_ad,
    "rcode":get_rcode,
    "opcode":get_opcode,
    "tc":get_tc,
    "z":get_z,
    "cd":get_cd,
    "rd":get_rd,
    "ra":get_ra,
}

if __name__ == "__main__":

    # basic func test
    flag = 0
    print_bits(flag)
    flag = set_qr(flag, codes.QR["response"])
    print_bits(flag)
    flag = set_opcode(flag, codes.OPCODE["notify"])
    print_bits(flag)

    flag = set_aa(flag, 1)
    flag = set_tc(flag, 1)
    flag = set_rd(flag, 1)
    flag = set_cd(flag,1)
    print_bits(flag)

    flag = set_rcode(flag, codes.RCODE["Refused"])
    print_bits(flag)
        
    # pack test
    flag = 0
    flag = pack_flag(flag, codes.QR["response"], codes.OPCODE["query"], 1, 1, 1, 0, 0, codes.RCODE["NoError"])
    print_bits(flag)
