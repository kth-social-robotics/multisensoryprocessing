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

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Get access to tobii live video streaming: rtsp://130.237.67.195:8554/live/eyes or scene

# Procees input data
def callback(_mq, get_shifted_time, routing_key, body):
    #json.load
    print(body)
    print("-------------------------------------------------")

mq = MessageQueue('mocaptobii_processing')

#mq.bind_queue(exchange='pre-processor', routing_key="{}.*".format(settings['messaging']['mocap_processing']), callback=callback)
mq.bind_queue(exchange='pre-processor', routing_key="{}.*".format(settings['messaging']['tobii_processing']), callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
