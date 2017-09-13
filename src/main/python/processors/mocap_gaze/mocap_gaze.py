# Get access to tobii live video streaming: rtsp://130.237.67.195:8554/live/eyes or scene

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

DEBUG = True

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Dictionaries
tobiimocap_dict = defaultdict(lambda : defaultdict(dict))

# Each key is the local timestamp in seconds. The second key is the frame
tobiimocap_dict[0][0]['device'] = 'body'

# Procees tobii input data
def tobiicallback(_mq, get_shifted_time, routing_key, body):
    if DEBUG: print("--------------------------------------------------------------------------------------------------")

    # Get tobii localtime
    tobiitime = body['localtime']

    # First get which second
    second = int(tobiitime)

    # Get decimals to decide which frame
    frame = int(math.modf(tobiitime)[0] * 50)

    # Put in dictionary
    tobiimocap_dict[second][frame][body['name']] = body

    # Print 1 frame before
    if DEBUG: print(tobiimocap_dict[second][frame-1])

# Procees mocap input data
def mocapcallback(_mq, get_shifted_time, routing_key, body):
    # Get mocap localtime
    mocaptime = body['localtime']

    # First get which second
    second = int(mocaptime)

    # Get decimals to decide which frame
    frame = int(math.modf(mocaptime)[0] * 50)

    # Put in dictionary
    tobiimocap_dict[second][frame]['mocap_' + body['name']] = body

mq = MessageQueue('mocaptobii_processing')

mq.bind_queue(exchange='pre-processor', routing_key="{}.*".format(settings['messaging']['tobii_processing']), callback=tobiicallback)
mq.bind_queue(exchange='pre-processor', routing_key="{}.*".format(settings['messaging']['mocap_processing']), callback=mocapcallback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
