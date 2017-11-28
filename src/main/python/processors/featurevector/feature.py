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
import matlab.engine
import subprocess
from subprocess import PIPE
import os
from os import system
import unicodedata
import mat4py as m4p

# Start matlab engine
mateng = matlab.engine.start_matlab()
mateng.addpath(r'/Users/diko/Dropbox/University/PhD/Code/MultiSensoryProcessing/multisensoryprocessing/src/main/matlab', nargout=0)
print("MATLAB")

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Define server
zmq_socket, zmq_server_addr = create_zmq_server()
mq = MessageQueue('feature-processor')

mq.publish(
    exchange='processor',
    routing_key=settings['messaging']['feature_processing'],
    body={'address': zmq_server_addr, 'file_type': 'txt'}
)

# Dictionaries
feature_dict = defaultdict(lambda : defaultdict(dict))

# Each key is the local timestamp in seconds. The second key is the frame
feature_dict[0][0]['device'] = 'body'

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

            if mocapbody:
                # Call Matlab script to calculate gazehits
                gaze_hits = mateng.gazehits(mocapbody)

                # If there are gaze hits count and filter by fixation (5 frames = 100ms)
                # Tobii 1
                if gaze_hits[0] != ['']:
                    print(localtime1, gaze_hits)

                # # Update dict values
                # tobiimocap_dict[second][frame-1]['tobii_glasses1']['gp3_3d'] = gaze_gp3
                # tobiimocap_dict[second][frame-1]['tobii_glasses1']['headpose'] = head_pose

                # Get mocap localtime
                #mocaptime = localtime1

                # First get which second
                #second = int(mocaptime)

                # Get decimals to decide which frame
                #frame = int(math.modf(mocaptime)[0] * 50)

                # Put in dictionary
                #feature_dict[second][frame]['mocap_' + mocapbody['name']] = mocapbody

                # Print 1 frame before
                #print(feature_dict[second][frame-1])
                #zmq_socket.send(msgpack.packb((tobiimocap_dict[second][frame-1], mq.get_shifted_time())))

    t1 = Thread(target = runA)
    t1.setDaemon(True)
    t1.start()
    #s1.close()

# Process nlp input data
def nlpcallback(_mq2, get_shifted_time2, routing_key2, body2):
    context2 = zmq.Context()
    s2 = context2.socket(zmq.SUB)
    s2.setsockopt_string(zmq.SUBSCRIBE, u'')
    s2.connect(body2.get('address'))

    def runB():
        while True:
            data2 = s2.recv()
            nlpbody, localtime2 = msgpack.unpackb(data2, use_list=False)

            nlpdata = {
                'verbs': nlpbody['language']['verbs'],
                'nouns': nlpbody['language']['nouns'],
                'adjectives': nlpbody['language']['adjectives']#,
                #'feedback': nlpbody['language']['feedback']
            }

            # Print event
            print(localtime2, nlpdata)

            # Get nlp localtime
            #nlptime = nlpbody['localtime']

            # First get which second
            #second = int(nlptime)

            # Get decimals to decide which frame
            #frame = int(math.modf(nlptime)[0] * 50)

            # Put in dictionary
            #feature_dict[second][frame]['tobii_' + tobiibody['name']] = tobiibody

    t2 = Thread(target = runB)
    t2.setDaemon(True)
    t2.start()
    #s2.close()

mq = MessageQueue('feature-processor')
mq.bind_queue(exchange='processor', routing_key=settings['messaging']['mocaptobii_processing'], callback=mocapcallback)
mq.bind_queue(exchange='processor', routing_key=settings['messaging']['nlp_data'], callback=nlpcallback)

mq.listen()

zmq_socket.send(b'CLOSE')
zmq_socket.close()
