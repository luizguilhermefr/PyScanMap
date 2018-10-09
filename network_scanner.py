import csv
import socket
import threading
import ping3

MASK_LEN = 32
BITS_PER_OCTET = 8
PORTS_PER_HOST = 2 ** 16


class NetworkScanner:
    def __init__(self, network, mask):
        self.network = network
        self.mask = mask
        self.port_map = {}
        with open('conf/ports.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                port, service, *_ = tuple(row)
                self.port_map[int(port)] = service

    def scan(self):
        bin_addr = self.address2bin(self.network)
        bin_mask = self.address2bin(self.mask)
        ones_count = sum(x == '1' for x in bin_mask)
        zeros_count = MASK_LEN - ones_count
        available_addresses = 2 ** zeros_count - 2

        net_address = self.make_valid_addresses(bin_addr[:ones_count], available_addresses)

        for address in net_address:
            try:
                latency = ping3.ping(address, use_exception=True)
                print('✔️ [%f] Host %s is alive. Checking ports...' % (latency, address))
                self.check_ports(address, latency)
            except (ping3.exception.TimeoutException, ping3.exception.DestinationUnreachableException,
                    ping3.exception.TimeToLiveExceededException):
                print('❌️ Host %s is not alive' % address)

    @staticmethod
    def fill_missing_octet_zeros(b):
        missing = BITS_PER_OCTET - len(b)
        return '0' * missing + b

    def address2bin(self, addr):
        return ''.join([self.fill_missing_octet_zeros(bin(int(n))[2:]) for n in addr.split('.')])

    @staticmethod
    def bin2address(b):
        parts = [b[:8], b[8:16], b[16:24], b[24:32]]
        return '.'.join([str(int(p, 2)) for p in parts])

    def make_valid_addresses(self, fixed_part, available_addresses):
        addresses = []
        for i in range(1, available_addresses + 1):
            var_part = self.fill_missing_octet_zeros(bin(i)[2:])
            addresses.append(self.bin2address(fixed_part + var_part))
        return addresses

    def check_ports(self, host, timeout):
        threads = []
        for port in range(0, PORTS_PER_HOST):
            thread = threading.Thread(target=self.check_port, args=(host, port, timeout * 1.5,))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def check_port(self, host, port, timeout):
        s = socket.socket()
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            service = 'unknown'
            if port in self.port_map:
                service = self.port_map[port]
            print('\t🆗 Port %d is open [%s].' % (port, service))
        except (socket.error, socket.herror, socket.timeout, socket.gaierror):
            pass
        finally:
            s.close()
