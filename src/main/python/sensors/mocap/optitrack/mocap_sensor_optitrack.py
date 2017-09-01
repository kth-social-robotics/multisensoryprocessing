import optirx as rx

dsock = rx.mkdatasock('130.237.67.209')
version = (2, 9, 0, 0)  # NatNet version to use
while True:
    data = dsock.recv(rx.MAX_PACKETSIZE)
    packet = rx.unpack(data, version=version)
    if type(packet) is rx.SenderData:
        version = packet.natnet_version
    print packet



# """OptiRX demo: connect to Optitrack on the same machine, print received data.
#
# Usage:
#
# python optrix_demo.py [number_of_packets_to_print] [natnet_version] [ip_addr]
#
# where natnet_version is 2500, 2600, 2700, 2900, 3000 etc
# for Motive 1.5, 1.6 betas, 1.7, 1.9, 1.10 respectively.
# """
#
#
# from __future__ import print_function
# import optirx as rx
# import sys
#
#
# def demo_recv_data():
#     # pretty-printer for parsed
#     try:
#         from simplejson import dumps, encoder
#         encoder.FLOAT_REPR = lambda o: ("%.4f" % o)
#     except ImportError:
#         from json import dumps, encoder
#         encoder.FLOAT_REPR = lambda o: ("%.4f" % o)
#
#     if "-h" in sys.argv[1:] or "--help" in sys.argv[1:]:
#         print(__doc__)
#         exit()
#
#     # the first optional command line argument:
#     # if given, the number of packets to dump
#     if sys.argv[1:]:
#         max_count = int(sys.argv[1])
#     else:
#         max_count = float("inf")
#
#     # the second optional command line argument
#     # is the version string of the NatNet server;
#     # may be necessary to receive data without
#     # the initial SenderData packet
#     if sys.argv[2:]:
#         version = tuple(map(int, sys.argv[2]))
#     else:
#         version = (3, 0, 0, 0)  # the latest SDK version
#
#     if sys.argv[3:]:
#         ip_addr = sys.argv[3]
#     else:
#         ip_addr = None
#
#     dsock = rx.mkdatasock(ip_addr)
#     count = 0
#     while count < max_count:
#         data = dsock.recv(rx.MAX_PACKETSIZE)
#         packet = rx.unpack(data, version=version)
#         if type(packet) is rx.SenderData:
#             version = packet.natnet_version
#             print("NatNet version received:", version)
#         if type(packet) in [rx.SenderData, rx.ModelDefs, rx.FrameOfData]:
#             print(dumps(packet._asdict(), indent=4))
#         count += 1
#
#
# if __name__ == "__main__":
#     demo_recv_data()



# import pika
# import sys
# import time
# import msgpack
# sys.path.append('../..')
# from shared import create_zmq_server, MessageQueue
# from subprocess import Popen, PIPE
# import yaml
#
# # Get platform
# if len(sys.argv) != 2:
#     exit('Error.')
# platform = sys.argv[1]
#
# # Print messages
# DEBUG = False
#
# # Settings
# SETTINGS_FILE = '../../settings.yaml'
#
# # Define server
# zmq_socket, zmq_server_addr = create_zmq_server()
# mq = MessageQueue('mocap-sensor')
#
# # Estabish la conneccion!
# settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())
# mq.publish(
#     exchange='sensors',
#     routing_key=settings['messaging']['new_sensor_mocap'],
#     body={'address': zmq_server_addr, 'file_type': 'txt'}
# )
#
# # Get mocap data stream
# if platform == 'mac':
#     process = Popen(['./vicon_mac/ViconDataStreamSDK_CPPTest', settings['messaging']['mocap_host']], stdout=PIPE, stderr=PIPE)
# elif platform == 'win64':
#     process = Popen(['./vicon_windows64/ViconDataStreamSDK_CPPTest.exe', settings['messaging']['mocap_host']], stdout=PIPE, stderr=PIPE)
#
# print('[*] Serving at {}. To exit press enter'.format(zmq_server_addr))
#
# # Send each data stream
# try:
#     frame = []
#     for stdout_line in iter(process.stdout.readline, ""):
#         #if DEBUG: print(stdout_line, "")
#         frame.append(stdout_line)
#
#         if stdout_line == 'Waiting for new frame...\n':
#             if DEBUG: print(frame)
#             zmq_socket.send(msgpack.packb((frame, mq.get_shifted_time())))
#             frame = []
#
# finally:
#     # Close connection
#     zmq_socket.send(b'CLOSE')
#     zmq_socket.close()
