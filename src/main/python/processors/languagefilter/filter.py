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
from os import system
import unicodedata

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Procees input data
def callback(_mq, get_shifted_time, routing_key, body):
    participant = routing_key.rsplit('.', 1)[1]

    # Say skills
    skills = []
    for x in body['language']['verbs']:
        skills.append(unicodedata.normalize('NFKD', x).encode('ascii','ignore'))
    system('say skills {}'.format(skills))
    # Say objects
    objects = []
    for x in body['language']['nouns']:
        objects.append(unicodedata.normalize('NFKD', x).encode('ascii','ignore'))
    system('say objects {}'.format(objects))
    # Say attributes
    attributes = []
    for x in body['language']['adjectives']:
        attributes.append(unicodedata.normalize('NFKD', x).encode('ascii','ignore'))
    system('say attributes {}'.format(attributes))
    # Say feedback
    feedback = []
    for x in body['language']['feedback']:
        feedback.append(unicodedata.normalize('NFKD', x).encode('ascii','ignore'))
    #system('say feedback {}'.format(feeback))
    #{u'adjectives': [u'red'], u'verbs': [u'pick'], u'feedback': [], u'nouns': [u'block']}

    data = {
        'skills': skills,
        'objects': objects,
        'attributes': attributes,
        'feedback': feedback
    }

    print(data)

    

    # _mq.publish(
    #     exchange='pre-processor',
    #     routing_key='nlp.data.{}'.format(participant),
    #     body=data
    # )

mq = MessageQueue('langfilter-processor')

routing_key1 = "{}.*".format(settings['messaging']['nlp_data'])
mq.bind_queue(exchange='pre-processor', routing_key=routing_key1, callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
