import zmq
import pika
import json
import time
import msgpack
import re
import sys
sys.path.append('..')
from shared import MessageQueue
import yaml
import os
import json
import msgpack
from collections import defaultdict
import datetime

# Settings
SETTINGS_FILE = '../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())


session_name = datetime.datetime.now().isoformat().replace('.', '_').replace(':', '_')

log_path = os.path.join(settings['logging']['asr_path'], session_name)

os.mkdir(log_path)


# Procees input data
def callback(ch, method, properties, body):
    # participant = routing_key.rsplit('.', 1)[1]
    path = os.path.join(log_path, '{}.txt'.format(method.routing_key))
    with open(path, 'ab') as f:
        f.write(msgpack.packb((method.exchange, method.routing_key, body)))
    print(method.exchange, method.routing_key, body)
    print("-------------------------------------------------")

mq = MessageQueue('asr-logger')

mq.bind_queue(exchange=settings['messaging']['pre_processing'], routing_key="*.*.*", callback_wrapper_func=callback)
mq.bind_queue(exchange=settings['messaging']['sensors'], routing_key="*.*.*", callback_wrapper_func=callback)
mq.bind_queue(exchange=settings['messaging']['wizard'], routing_key="*.*.*", callback_wrapper_func=callback)
mq.bind_queue(exchange=settings['messaging']['environment'], routing_key="*.*.*", callback_wrapper_func=callback)
mq.bind_queue(exchange=settings['messaging']['fatima'], routing_key="*.*.*", callback_wrapper_func=callback)


print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
