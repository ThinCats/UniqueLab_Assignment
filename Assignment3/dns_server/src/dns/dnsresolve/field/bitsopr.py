
"""
This is for bits opr
For 0x0000
We assume that it's only for 2 bytes opr
"""

# From left to right is from start to end
# mask is 00001100
def get_bits(target, start=0, end=0):
    # mask_lower = (0xffff) << start
    # mask_higher = (0xffff) << end
    # print_bits(mask_higher)
    
    end += 1
    return (target & (((0xffff)<< start) ^ ((0xffff) << end))) >> start

# Put val in the postion
# mask is 11110011
def set_bits(target, val, start, end=None):
    # [start, end)
    if end == None:
        end = len(bin(val)) - 2 + start
    
    end += 1
    # mask = (((0xffff) << start) ^ ((0xffff) << end)) & 0xffff
    # print(bin(mask))
    # val = val << start
    # print_bits(val)
    # print_bits(~(((0xffff) << start) ^ ((0xffff) << end)))
    return (target & ~(((0xffff) << start) ^ ((0xffff) << end))) | (val << start)

# To print unsigned int
def print_bits(target):
    print(bin(target & 0xffff))
if __name__ == '__main__':
    # print_bits(set_bits(0, 0, 0))
    # print_bits(set_bits(0, 3, 0))
    print_bits(1111)
    print_bits(set_bits(1111, 0, 0, 0))
    # print_bits(111)
    # print_bits(get_bits(111, 3, 4))
    

