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
import subprocess
from subprocess import PIPE
import os

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Procees input data
def callback(_mq, get_shifted_time, routing_key, body):
    participant = routing_key.rsplit('.', 1)[1]

    print(body)

    # data = {
    #     'speech': body['text'],
    #     'language': syntax,
    #     'timestamps': body['timestamps']
    # }

    # nlp_data = settings['messaging']['nlp_data']
    # key = '{}.{}'.format(nlp_data, participant)
    # _mq.publish(
    #     exchange='processor',
    #     routing_key=key,
    #     body=data
    # )

mq = MessageQueue('langfilter-processor')

routing_key1 = "{}.*".format(settings['messaging']['nlp_data'])
mq.bind_queue(exchange='processor', routing_key=routing_key1, callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
