import pika
import sys
import time
import msgpack
sys.path.append('../../..')
from shared import create_zmq_server, MessageQueue
from subprocess import Popen, PIPE
import yaml
import optirx as rx

# Get mocap IP
if len(sys.argv) != 2:
    exit('Error.')
mocap_ip = sys.argv[1]

# Print messages
DEBUG = True

# Settings
SETTINGS_FILE = '../../../settings.yaml'

# Define server
zmq_socket, zmq_server_addr = create_zmq_server()
mq = MessageQueue('mocap-sensor')

# Estabish la conneccion!
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())
mq.publish(
    exchange='sensors',
    routing_key=settings['messaging']['new_sensor_mocap'],
    body={'address': zmq_server_addr, 'file_type': 'txt'}
)

# Pretty-printer for parsed
try:
    from simplejson import dumps, encoder
    encoder.FLOAT_REPR = lambda o: ("%.4f" % o)
except ImportError:
    from json import dumps, encoder
    encoder.FLOAT_REPR = lambda o: ("%.4f" % o)

# Get mocap data stream
dsock = rx.mkdatasock(mocap_ip)
version = (2, 9, 0, 0)  # NatNet version to use
while True:
    data = dsock.recv(rx.MAX_PACKETSIZE)
    packet = rx.unpack(data, version=version)
    if type(packet) is rx.SenderData:
        version = packet.natnet_version
    frame = dumps(str(packet._asdict()), indent=4)
    if DEBUG: print(frame)

print('[*] Serving at {}. To exit press enter'.format(zmq_server_addr))

# Send each data stream
try:
    zmq_socket.send(msgpack.packb((frame, time.time())))
finally:
    # Close connection
    zmq_socket.send(b'CLOSE')
    zmq_socket.close()
