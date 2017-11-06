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
from client import Client

if len(sys.argv) != 2:
    exit('please supply ip')
server_ip = sys.argv[1]

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Create pipes to communicate to the client process
pipe_in_client, pipe_out = os.pipe()
pipe_in, pipe_out_client = os.pipe()

# Create a "name" for the client, so that other clients can access by that name
my_client_type = "the_architecture"

# Create a client object to communicate with the server
client = Client(client_type=my_client_type,
                pipe_in=pipe_in_client,
                pipe_out=pipe_out_client,
                host=server_ip)

# Start the client-process
client.start()

# Procees input data
def callback(_mq, get_shifted_time, routing_key, body):
    participant = routing_key.rsplit('.', 1)[1]

    # Gather skills
    skills = []
    for x in body['language']['verbs']:
        skills.append(unicodedata.normalize('NFKD', x).encode('ascii','ignore'))

    # Gather objects
    objects = []
    for x in body['language']['nouns']:
        objects.append(unicodedata.normalize('NFKD', x).encode('ascii','ignore'))

    # Gather attributes
    attributes = []
    for x in body['language']['adjectives']:
        attributes.append(unicodedata.normalize('NFKD', x).encode('ascii','ignore'))

    # Gather feedback
    feedback = []
    for x in body['language']['feedback']:
        feedback.append(unicodedata.normalize('NFKD', x).encode('ascii','ignore'))

    data = {
        'skills': skills,
        'objects': objects,
        'attributes': attributes,
        'feedback': feedback
    }

    # Print and say data
    #print(data)
    #system('say skills {}'.format(skills))
    #system('say objects {}'.format(objects))
    #system('say attributes {}'.format(attributes))
    #system('say feedback {}'.format(feeback))

    # Sending messages
    my_message = str(data)
    my_message = "interpreter;" + my_message + "$"
    print(my_message)

    # Encode the string to utf-8 and write it to the pipe defined above
    os.write(pipe_out, my_message.encode("utf-8"))
    sys.stdout.flush()

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

# Close the client safely, not always necessary
client.close() # Tell it to close
client.join() # Wait for it to close
