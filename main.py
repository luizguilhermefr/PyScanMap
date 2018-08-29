import sys

ARG_COUNT = 3
MASK_LEN = 32


def fill_missing_zeros(b):
    missing = 8 - len(b)
    return '0' * missing + b

def address2bin(addr):
    return ''.join([fill_missing_zeros(bin(int(n))[2:]) for n in addr.split('.')])


def bin2address(b):
    parts = [b[:8], b[8:16], b[16:24], b[24:32]]
    return '.'.join([str(int(p, 2)) for p in parts])


def make_valid_addresses(fixed_part, available_addresses):
    address = []
    for i in range(1, available_addresses + 1):
        var_part = fill_missing_zeros(bin(i)[2:])
        address.append(bin2address(fixed_part + var_part))
    return address


if len(sys.argv) != ARG_COUNT:
    raise Exception("Invalid parameters.")

address = sys.argv[1]
mask = sys.argv[2]

bin_addr = address2bin(address)
bin_mask = address2bin(mask)
ones_count = sum(x == '1' for x in bin_mask)
zeros_count = MASK_LEN - ones_count
available_addresses = 2 ** zeros_count - 2

net_address = make_valid_addresses(bin_addr[:ones_count], available_addresses)

print(net_address)