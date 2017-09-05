'''
    Example for how to send and receive discovery info from glasses on network.

    Note: This example program is tested with Python 2.7 on Ubuntu 12.04 LTS (precise),
          Ubuntu 14.04 LTS (trusty), and Windows 8. 
'''
import socket
import struct

MULTICAST_ADDR = 'ff02::1'  # ipv6: all nodes on the local network segment
PORT = 13007


if __name__ == '__main__':

    s6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    s6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s6.bind(('::', PORT))

    s6.sendto('{"type":"discover"}', (MULTICAST_ADDR, 13006))

    print ("Press Ctrl-C to abort...")
    while True:
        data, address = s6.recvfrom(1024)
        print (" From: " + address[0] + " " + data)
