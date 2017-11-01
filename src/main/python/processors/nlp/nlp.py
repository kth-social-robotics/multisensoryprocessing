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

# Procees input data
def callback(_mq, get_shifted_time, routing_key, body):
    participant = routing_key.rsplit('.', 1)[1]

    print(body)

    # data = {
    #     'position': position,
    #     'timestamps': body['timestamps']
    # }
    # position_data = settings['messaging']['position_data']
    # key = '{}.{}'.format(position_data, participant)
    # _mq.publish(
    #     exchange='pre-processor',
    #     routing_key=key,
    #     body=data
    # )

mq = MessageQueue('nlp-processor')

routing_key1 = "{}.*".format(settings['messaging']['asr_watson'])
print(routing_key1)

mq.bind_queue(exchange='pre-processor', routing_key=routing_key1, callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
