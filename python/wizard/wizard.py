# python3 wizard.py [agent] [condition]

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

# Settings
SETTINGS_FILE = '../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Get condition flag
if len(sys.argv) != 3:
    exit('Error. Enter condition flag')
agent = sys.argv[1]
condition = sys.argv[2]

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
    print("--------------------")
    print("Robot Actions:")
    print("1. Start Interaction")
    print("2. Next Step")
    print("3. End Interaction")
    print("--------------------")
    print("User Actions:")
    print("4. Correct Action")
    print("5. Wrong Action")
    print("6. Speech-Where")
    print("7. Speech-Which")
    print("8. Speech-Repeat")
    print("9. Gaze-Object")
    print("10. Gaze-Other")
    print("11. Gaze-Robot")
    print("--------------------")

    # Get current key
    key = input('Press: ')

    data = {
        'agent': agent,
        'condition': condition,
        'action': key
    }

    # Print message
    print("STATUS")
    print(data)

    zmq_socket.send(msgpack.packb((data, mq.get_shifted_time())))

mq = MessageQueue('wizard-processor')

zmq_socket.send(b'CLOSE')
zmq_socket.close()
