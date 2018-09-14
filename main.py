import sys
import re
import argparse

from network_scanner import NetworkScanner

VERSION = '1.0'
IPV4_REGEX = "^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
IPV6_REGEX = "(?<![:.\w])(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}(?![:.\w])"


def validate_arguments(network, mask):
    if not re.compile(IPV4_REGEX).match(network):
        if re.compile(IPV6_REGEX).match(network):
            raise Exception("IPv6 is not supported. Please provide a valid IPv4 address for network.")
        raise Exception("Please provide a valid IPv4 address for network.")

    if not re.compile(IPV4_REGEX).match(mask):
        raise Exception("Please provide a valid IPv4 mask.")


def main():
    parser = argparse.ArgumentParser(
        prog='pyscanmap',
        description='PyScanMap makes it easy to scan your network hosts and their open ports',
        epilog='By Luiz Rosa & Renan Tashiro'
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s ' + VERSION
    )
    parser.add_argument(
        '-n',
        '--network',
        help='IPv4 address for the network'
    )
    parser.add_argument(
        '-m',
        '--mask',
        help='Mask for the IPv4 address, expressed as an IPv4 address'
    )
    args = parser.parse_args(sys.argv[1:])
    validate_arguments(args.network, args.mask)

    network_scanner = NetworkScanner(args.network, args.mask)
    network_scanner.scan()


if __name__ == '__main__':
    main()
