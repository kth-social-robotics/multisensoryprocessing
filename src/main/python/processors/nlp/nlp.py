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

    def calc_syntaxnet(x):
        p = subprocess.Popen(('docker', 'run', '--rm', '-i', 'brianlow/syntaxnet'), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(x)
        adjectives = set(re.findall('\+\-\- (.*) (?:JJ|JJR|JJS)', stdout))
        nouns = set(re.findall('\+\-\- (.*) (?:NN|NNS|NNP|NNPS)', stdout))
        verbs0 = set(re.findall('(.*) (?:VB|VBD|VBG|VBN|VBP|VBZ)', stdout))
        verbs = set()
        confirmation = set(re.findall('(yes|yeah|no)', stdout))
        for i in verbs0:
            matched = re.match('\s*\+\-\-\s+(.+)', i)
            if matched:
                verbs.add(matched.group(1))
            else:
                verbs.add(i)
        syntaxdata = {
            'verbs': list(verbs),
            'adjectives': list(adjectives),
            'nouns': list(nouns),
            'feedback': list(confirmation)
        }
        return syntaxdata

    syntax = calc_syntaxnet(body['text'])

    data = {
        'speech': body['text'],
        'language': syntax
    }

    #print(data['language'])

    _mq.publish(
        exchange='pre-processor',
        routing_key='nlp.data.{}'.format(participant),
        body=data
    )

mq = MessageQueue('nlp-processor')

routing_key1 = "{}.*".format(settings['messaging']['asr_watson'])
mq.bind_queue(exchange='pre-processor', routing_key=routing_key1, callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()