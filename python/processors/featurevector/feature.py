# python feature.py 130.237.67.209
# Wait for Matlab to start

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
import numpy
from client import Client

if len(sys.argv) != 2:
    exit('Please supply ROS server IP')
server_ip = sys.argv[1]

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
# Time, Frame: P1 Gaze, P2 Gaze, P1 Holding object, P1 Np, P1 Adj, P1 Verb
feature_dict[0][0]['P1G'] = ''
#feature_dict[0][0]['P2G'] = ''
feature_dict[0][0]['P1GP'] = ''
#feature_dict[0][0]['P2GP'] = ''
feature_dict[0][0]['P1H'] = ''
#feature_dict[0][0]['P2H'] = ''
feature_dict[0][0]['P1N'] = ''
feature_dict[0][0]['P1A'] = ''
feature_dict[0][0]['P1V'] = ''
feature_dict[0][0]['P1F'] = ''
#feature_dict[0][0]['P2N'] = ''
#feature_dict[0][0]['P2A'] = ''
#feature_dict[0][0]['P2V'] = ''
#feature_dict[0][0]['P2F'] = ''

# Procees mocap input data
def mocapcallback(_mq1, get_shifted_time1, routing_key1, body1):
    context1 = zmq.Context()
    s1 = context1.socket(zmq.SUB)
    s1.setsockopt_string(zmq.SUBSCRIBE, u'')
    s1.connect(body1.get('address'))

    def runA():
        # Fixation filter
        fixfilter = 0

        while True:
            data1 = s1.recv()
            mocapbody, localtime1 = msgpack.unpackb(data1, use_list=False)

            if mocapbody:
                object1 = 0
                object2 = 0
                hand1l = 0
                hand1r = 0
                table1 = 0

                # Get objects
                if 'mocap_target1' in mocapbody:
                    object1 = numpy.array((mocapbody['mocap_target1']['position']['x'], mocapbody['mocap_target1']['position']['y'], mocapbody['mocap_target1']['position']['z']))
                if 'mocap_target2' in mocapbody:
                    object2 = numpy.array((mocapbody['mocap_target2']['position']['x'], mocapbody['mocap_target2']['position']['y'], mocapbody['mocap_target2']['position']['z']))
                if 'mocap_hand1l' in mocapbody:
                    hand1l = numpy.array((mocapbody['mocap_hand1l']['position']['x'], mocapbody['mocap_hand1l']['position']['y'], mocapbody['mocap_hand1l']['position']['z']))
                if 'mocap_hand1r' in mocapbody:
                    hand1r = numpy.array((mocapbody['mocap_hand1r']['position']['x'], mocapbody['mocap_hand1r']['position']['y'], mocapbody['mocap_hand1r']['position']['z']))
                if 'mocap_table1' in mocapbody:
                    table1 = numpy.array((mocapbody['mocap_table1']['position']['x'], mocapbody['mocap_table1']['position']['y'], mocapbody['mocap_table1']['position']['z']))

                # Calculate object holdings
                dist_h1r_o2 = 0
                dist_h1r_tab1 = 0

                # Calculate distance between hand1r and object 2
                dist_h1r_o2 = numpy.linalg.norm(hand1r - object2)

                # Calculate distance between hand1r and table 1
                dist_h1r_tab1 = numpy.linalg.norm(hand1r - table1)

                # Get mocap localtime
                mocaptime = localtime1

                # First get which second
                second = int(mocaptime)

                # Get decimals to decide which frame
                frame = int(math.modf(mocaptime)[0] * 50)

                # If less than 15cm put in feature vector
                if dist_h1r_o2 != 0 and dist_h1r_o2 < 0.15:
                    # Put in dictionary
                    feature_dict[second][frame]['P1H'] = 'O2'

                    # Print frame
                    print(feature_dict[second][frame])
                    #zmq_socket.send(msgpack.packb((tobiimocap_dict[second][frame-1], mq.get_shifted_time())))

                    # Sending messages to ROS
                    my_message = json.dumps(feature_dict[second][frame])
                    my_message = "interpreter;data;" + my_message + "$"
                    #print(my_message)

                    # Encode the string to utf-8 and write it to the pipe defined above
                    os.write(pipe_out, my_message.encode("utf-8"))
                    sys.stdout.flush()

                    # Remove from dict
                    feature_dict[second].pop(frame-10, None)

                if dist_h1r_tab1 != 0 and dist_h1r_tab1 < 0.30:
                    # Put in dictionary
                    feature_dict[second][frame]['P1H'] = 'T'

                    # Print frame
                    print(feature_dict[second][frame])
                    #zmq_socket.send(msgpack.packb((tobiimocap_dict[second][frame-1], mq.get_shifted_time())))

                    # Sending messages to ROS
                    my_message = json.dumps(feature_dict[second][frame])
                    my_message = "interpreter;data;" + my_message + "$"
                    #print(my_message)

                    # Encode the string to utf-8 and write it to the pipe defined above
                    os.write(pipe_out, my_message.encode("utf-8"))
                    sys.stdout.flush()

                    # Remove from dict
                    feature_dict[second].pop(frame-10, None)

                # Call Matlab script to calculate gazehits
                gaze_hits = mateng.gazehits(mocapbody)

                # Get mocap localtime
                mocaptime = localtime1

                # First get which second
                second = int(mocaptime)

                # Get decimals to decide which frame
                frame = int(math.modf(mocaptime)[0] * 50)

                # Vision system point bottom right: x = 0.65, y = 0.34
                # Mocap system point bottom right: x = -2.81, z = 4.19
                # xrobot = -zmocap (-3.54)
                # yrobot = -xmocap (+3.15)

                # Table Tobii 1 gaze position
                if gaze_hits[0] == 'T1':
                    xrobot = 0.65 - (gaze_hits[1][0][0] - 4.19) # xrobot - (xcurrent - xmocap)
                    yrobot = 0.34 - (gaze_hits[1][0][2] + 2.81) # yrobot - (ycurrent + ymocap)

                    # Put in dictionary
                    feature_dict[second][frame]['P1GP'] = [xrobot, yrobot]

                    # # Print frame
                    # print(feature_dict[second][frame])
                    # #zmq_socket.send(msgpack.packb((tobiimocap_dict[second][frame-1], mq.get_shifted_time())))
                    #
                    # # Sending messages to ROS
                    # my_message = json.dumps(feature_dict[second][frame])
                    # my_message = "interpreter;data;" + my_message + "$"
                    # #print(my_message)
                    #
                    # # Encode the string to utf-8 and write it to the pipe defined above
                    # os.write(pipe_out, my_message.encode("utf-8"))
                    # sys.stdout.flush()
                    #
                    # # Remove from dict
                    # feature_dict[second].pop(frame-10, None)

                # Tobii 1
                if gaze_hits[0] != ['']:
                    # Put in dictionary
                    feature_dict[second][frame]['P1G'] = gaze_hits[0]

                    # # Count and filter by fixation (5 frames = 100ms, 10 frames = 200ms)
                    # for x in range(1, 10):
                    #     if feature_dict[second][frame] == feature_dict[second][frame-x]:
                    #         fixfilter = fixfilter + 1
                    #     else:
                    #         fixfilter = 0

                    # Print frame
                    #if fixfilter == 9:
                        #fixfilter = 0
                        #print(feature_dict[second][frame])
                        #zmq_socket.send(msgpack.packb((tobiimocap_dict[second][frame-1], mq.get_shifted_time())))

                    # Print frame
                    print(feature_dict[second][frame])
                    #zmq_socket.send(msgpack.packb((tobiimocap_dict[second][frame-1], mq.get_shifted_time())))

                    # Sending messages to ROS
                    my_message = json.dumps(feature_dict[second][frame])
                    my_message = "interpreter;data;" + my_message + "$"
                    #print(my_message)

                    # Encode the string to utf-8 and write it to the pipe defined above
                    os.write(pipe_out, my_message.encode("utf-8"))
                    sys.stdout.flush()

                    # Remove from dict
                    feature_dict[second].pop(frame-10, None)

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
                'adjectives': nlpbody['language']['adjectives'],
                'feedback': nlpbody['language']['feedback']
            }

            # Get nlp localtime
            nlptime = localtime2

            # First get which second
            second = int(nlptime)

            # Get decimals to decide which frame
            frame = int(math.modf(nlptime)[0] * 50)

            # Put in dictionary
            feature_dict[second][frame]['P1N'] = nlpbody['language']['nouns']
            feature_dict[second][frame]['P1A'] = nlpbody['language']['adjectives']
            feature_dict[second][frame]['P1V'] = nlpbody['language']['verbs']
            feature_dict[second][frame]['P1F'] = nlpbody['language']['feedback']

            # Print feature vector
            print(feature_dict[second][frame])
            #zmq_socket.send(msgpack.packb((tobiimocap_dict[second][frame-1], mq.get_shifted_time())))

            # Sending messages to ROS
            my_message = json.dumps(feature_dict[second][frame])
            my_message = "interpreter;data;" + my_message + "$"
            #print(my_message)

            # Encode the string to utf-8 and write it to the pipe defined above
            os.write(pipe_out, my_message.encode("utf-8"))
            sys.stdout.flush()

            # Remove value from dict
            feature_dict[second].pop(frame-10, None)

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

# Close the client safely, not always necessary
client.close() # Tell it to close
client.join() # Wait for it to close
