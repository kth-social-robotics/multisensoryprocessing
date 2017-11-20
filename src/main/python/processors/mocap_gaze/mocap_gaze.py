# Get access to tobii live video streaming: rtsp://130.237.67.195:8554/live/eyes or scene
# websocketd --port=8080 python mocap_gaze.py

import zmq
import pika
import json
import time
import msgpack
import re
import sys
sys.path.append('../..')
from shared import MessageQueue
import yaml
from collections import defaultdict
import math
from shared import create_zmq_server, MessageQueue
from threading import Thread

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Define server
zmq_socket, zmq_server_addr = create_zmq_server()
mq = MessageQueue('mocaptobii-processor')

mq.publish(
    exchange='processor',
    routing_key=settings['messaging']['mocaptobii_processing'],
    body={'address': zmq_server_addr, 'file_type': 'txt'}
)

# Dictionaries
tobiimocap_dict = defaultdict(lambda : defaultdict(dict))

# Each key is the local timestamp in seconds. The second key is the frame
tobiimocap_dict[0][0]['device'] = 'body'

# Procees mocap input data
def mocapcallback(_mq1, get_shifted_time1, routing_key1, body1):
    context1 = zmq.Context()
    s1 = context1.socket(zmq.SUB)
    s1.setsockopt_string(zmq.SUBSCRIBE, u'')
    s1.connect(body1.get('address'))

    def runA():
        while True:
            data1 = s1.recv()
            mocapbody, localtime1 = msgpack.unpackb(data1, use_list=False)

            # Get mocap localtime
            mocaptime = mocapbody['localtime']

            # First get which second
            second = int(mocaptime)

            # Get decimals to decide which frame
            frame = int(math.modf(mocaptime)[0] * 50)

            # Put in dictionary
            tobiimocap_dict[second][frame]['mocap_' + mocapbody['name']] = mocapbody

            # Print 1 frame before
            print(tobiimocap_dict[second][frame-1])

            #key = settings['messaging']['mocaptobii_processing']
            #_mq.publish(exchange='processor', routing_key=key, body=tobiimocap_dict[second][frame-1])

    t1 = Thread(target = runA)
    t1.setDaemon(True)
    t1.start()
    #s1.close()

# Procees tobii input data
def tobiicallback(_mq2, get_shifted_time2, routing_key2, body2):
    context2 = zmq.Context()
    s2 = context2.socket(zmq.SUB)
    s2.setsockopt_string(zmq.SUBSCRIBE, u'')
    s2.connect(body2.get('address'))

    def runB():
        while True:
            data2 = s2.recv()
            tobiibody, localtime2 = msgpack.unpackb(data2, use_list=False)

            # Get tobii localtime
            tobiitime = tobiibody['localtime']

            # First get which second
            second = int(tobiitime)

            # Get decimals to decide which frame
            frame = int(math.modf(tobiitime)[0] * 50)

            # Put in dictionary
            tobiimocap_dict[second][frame]['tobii_' + tobiibody['name']] = tobiibody

    t2 = Thread(target = runB)
    t2.setDaemon(True)
    t2.start()
    #s2.close()

mq = MessageQueue('mocaptobii-processor')
mq.bind_queue(exchange='pre-processor', routing_key=settings['messaging']['mocap_processing'], callback=mocapcallback)
mq.bind_queue(exchange='pre-processor', routing_key=settings['messaging']['tobii_processing'], callback=tobiicallback)

mq.listen()

zmq_socket.send(b'CLOSE')
zmq_socket.close()
