import socket
from ping3 import ping

MASK_LEN = 32
BITS_PER_OCTET = 8
PORTS_PER_HOST = 2 ** 16


class NetworkScanner:
    def __init__(self, network, mask):
        self.network = network
        self.mask = mask

    def scan(self):
        bin_addr = self.address2bin(self.network)
        bin_mask = self.address2bin(self.mask)
        ones_count = sum(x == '1' for x in bin_mask)
        zeros_count = MASK_LEN - ones_count
        available_addresses = 2 ** zeros_count - 2

        net_address = self.make_valid_addresses(bin_addr[:ones_count], available_addresses)

        for address in net_address:
            latency = ping(address, ttl=1)
            if latency is None:
                print('❌️ Host %s is not alive' % address)
            else:
                print('✔️ [%fs] Host %s is alive. Checking ports...' % (latency, address))
                ports_alive = self.check_ports(address, latency)
                for port in ports_alive:
                    print('🆗 Port %d is open.' % port)

    def fill_missing_octet_zeros(self, b):
        missing = BITS_PER_OCTET - len(b)
        return '0' * missing + b

    def address2bin(self, addr):
        return ''.join([self.fill_missing_octet_zeros(bin(int(n))[2:]) for n in addr.split('.')])

    def bin2address(self, b):
        parts = [b[:8], b[8:16], b[16:24], b[24:32]]
        return '.'.join([str(int(p, 2)) for p in parts])

    def make_valid_addresses(self, fixed_part, available_addresses):
        addresses = []
        for i in range(1, available_addresses + 1):
            var_part = self.fill_missing_octet_zeros(bin(i)[2:])
            addresses.append(self.bin2address(fixed_part + var_part))
        return addresses

    def check_ports(self, host, timeout):
        ports_alive = []
        for port in range(0, PORTS_PER_HOST + 1):
            if self.check_port(host, port, timeout * 1.5):
                ports_alive.append(port)
        return ports_alive

    def check_port(self, host, port, timeout):
        s = socket.socket()
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            status = True
        except:
            status = False
        s.close()
        return status
