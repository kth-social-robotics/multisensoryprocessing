# python3 wizard.py [condition]

import zmq
import pika
import json
import json.decoder
import time
import msgpack
import re
import sys
sys.path.append('..')
from shared import MessageQueue
import yaml
import subprocess
from subprocess import PIPE
import os
from shared import create_zmq_server, MessageQueue

# Print messages
DEBUG = True

# Settings
SETTINGS_FILE = '../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Get condition flag
if len(sys.argv) != 2:
    exit('Error. Enter condition flag')
conditionflag = sys.argv[1]

# Define server
zmq_socket, zmq_server_addr = create_zmq_server()
mq = MessageQueue('wizard-processor')

mq.publish(
    exchange='processor',
    routing_key=settings['messaging']['wizard_data'],
    body={'address': zmq_server_addr, 'file_type': 'txt'}
)

while True:
    # Print actions
    print("Actions:")
    print("1. Start")
    print("2. End")

    # Get current key
    key = input('Press: ')

    data = {
        'condition': conditionflag,
        'action': key
    }

    if DEBUG: print(data)

    zmq_socket.send(msgpack.packb((data, mq.get_shifted_time())))

mq = MessageQueue('wizard-processor')

zmq_socket.send(b'CLOSE')
zmq_socket.close()
