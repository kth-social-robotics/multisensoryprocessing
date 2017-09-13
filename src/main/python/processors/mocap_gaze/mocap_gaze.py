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

DEBUG = True

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Dictionaries
tobiimocap_dict = defaultdict(lambda : defaultdict(dict))
tobiimocap_dict[0]['0'] = '0'

# Procees tobii input data
def tobiicallback(_mq, get_shifted_time, routing_key, body):
    if DEBUG:
        print("-------------------------------------------------Tobii-------------------------------------------------")
        tobiitime = body['localtime']
        tobiimocap_dict[tobiitime]['tobii'] = body
        print(tobiimocap_dict[tobiitime])

# Procees mocap input data
def mocapcallback(_mq, get_shifted_time, routing_key, body):
    if DEBUG:
        print("-------------------------------------------------Mocap-------------------------------------------------")
        mocaptime = body['localtime']
        tobiimocap_dict[mocaptime]['mocap'] = body
        print(tobiimocap_dict[mocaptime])

mq = MessageQueue('mocaptobii_processing')

mq.bind_queue(exchange='pre-processor', routing_key="{}.*".format(settings['messaging']['tobii_processing']), callback=tobiicallback)
mq.bind_queue(exchange='pre-processor', routing_key="{}.*".format(settings['messaging']['mocap_processing']), callback=mocapcallback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
