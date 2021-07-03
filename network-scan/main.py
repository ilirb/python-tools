#!/usr/bin/env python3

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import socket


def check_server(address, ports):
    open_ports = []
    for port in ports:
        try:
            s = socket.socket()
            s.settimeout(1)
            s.connect((address, port))
            open_ports.append(port)
            s.close()
            continue
        except:
            s.close()
    return open_ports


def scan_network(args):
    startts = time.time()
    subnet = args.net
    ports = args.ports
    online_ips = {}

    subnet_class = subnet.split('.')
    ips = []

    if len(subnet_class) == 2:
        for c in range(0, 255):
            for i in range(1, 255):
                ips.append(f"{subnet}.{c}.{i}")

    elif len(subnet_class) == 3:
        for i in range(1, 255):
            ips.append(f"{subnet}.{i}")

    elif len(subnet_class) == 4:
        ips.append(subnet)

    else:
        exit()

    future_to_ip = {executor.submit(check_server, ip, ports): ip for ip in ips}

    print("IP\t\tOpen Ports")
    print("================")

    for future in as_completed(future_to_ip):
        ip = future_to_ip[future]
        try:
            data = future.result()
        except Exception as exc:
            print (f'{ip} generated an exception: {exc}')
        if data:
            online_ips[ip] = data
            print(f"{ip}\t{data}")

    print("================")
    endts = round((time.time() - startts), 3)
    print(f"Scanning took: {endts} sec")

    # Unused dict
    # print(online_ips)


if __name__ == '__main__':
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description='''
        A fast class network port scanner.
        Enter partial IP address e.g. 192.168.0 to scan all IPs in 192.168.0.[1-255];
        10.0 to scan all IPs in 10.0.[0-255].[1-255]
    ''')
    parser.add_argument('-n', '--net', help='Partial IP, e.g. (192.168.0)', required=True)
    parser.add_argument('-p', '--ports', nargs='+', type=int, help='Enter multiple Port(s) to scan for', required=True)
    parser.add_argument('-t', '--threads', help='Number of simultaneous threads, default 255', type=int, default=255)
    parser.set_defaults(func=scan_network)

    args = parser.parse_args()

    number_of_threads = args.threads
    executor = ThreadPoolExecutor(number_of_threads)

    args.func(args)
