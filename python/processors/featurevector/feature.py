# python feature.py 130.237.67.209 furhat
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

if len(sys.argv) != 3:
    exit('Please supply server IP and agent')
server_ip = sys.argv[1]
agent = sys.argv[2]

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
mateng.addpath(r'/Users/diko/Dropbox/University/PhD/Code/MultiSensoryProcessing/multisensoryprocessing/matlab', nargout=0)
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
# Time, Frame: Timestamp, P1 Np, P1 Adj, P1 Verb, P1 Det, P1 Pron, P1 Feedback, P1 ASR, P1 Gaze, P2 Gaze, P1 Gaze Angle, P2 Gaze Angle, P1 Holding object, Step
feature_dict[0][0]['TS'] = ''
feature_dict[0][0]['P1N'] = ''
feature_dict[0][0]['P1A'] = ''
feature_dict[0][0]['P1V'] = ''
feature_dict[0][0]['P1D'] = ''
feature_dict[0][0]['P1P'] = ''
feature_dict[0][0]['P1F'] = ''
feature_dict[0][0]['P1ASR'] = ''
feature_dict[0][0]['P1G'] = ''
feature_dict[0][0]['P2G'] = ''
feature_dict[0][0]['P1GA'] = ''
feature_dict[0][0]['P2GA'] = ''
feature_dict[0][0]['P1H'] = ''
feature_dict[0][0]['S'] = ''

glasses_num = 2
gloves_num = 1
targets_num = 5
tables_num = 2

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

            # Get mocap localtime
            mocaptime = localtime1

            # First get which second
            second = int(mocaptime)

            # Get decimals to decide which frame
            frame = int(math.modf(mocaptime)[0] * 50)

            # Check that data is received
            if mocapbody:
                # Initiate objects
                handl = []
                handr = []
                target = []
                table = []
                # Hands
                for x in range(0, gloves_num):
                    handl.append(0)
                    handr.append(0)
                # Targets
                for x in range(0, targets_num):
                    target.append(0)
                # Tables
                for x in range(0, tables_num):
                    table.append(0)

                # Get objects
                # Hands
                for x in range(0, gloves_num):
                    if 'mocap_hand' + str(x + 1) + 'l' in mocapbody:
                        handl[x] = numpy.array((mocapbody['mocap_hand' + str(x + 1) + 'l']['position']['x'], mocapbody['mocap_hand' + str(x + 1) + 'l']['position']['y'], mocapbody['mocap_hand' + str(x + 1) + 'l']['position']['z']))
                    if 'mocap_hand' + str(x + 1) + 'r' in mocapbody:
                        handr[x] = numpy.array((mocapbody['mocap_hand' + str(x + 1) + 'r']['position']['x'], mocapbody['mocap_hand' + str(x + 1) + 'r']['position']['y'], mocapbody['mocap_hand' + str(x + 1) + 'r']['position']['z']))
                # Targets
                for x in range(0, targets_num):
                    if 'mocap_target' + str(x + 1) in mocapbody:
                        target[x] = numpy.array((mocapbody['mocap_target' + str(x + 1)]['position']['x'], mocapbody['mocap_target' + str(x + 1)]['position']['y'], mocapbody['mocap_target' + str(x + 1)]['position']['z']))
                # Tables
                for x in range(0, tables_num):
                    if 'mocap_table' + str(x + 1) in mocapbody:
                        table[x] = numpy.array((mocapbody['mocap_table' + str(x + 1)]['position']['x'], mocapbody['mocap_table' + str(x + 1)]['position']['y'], mocapbody['mocap_table' + str(x + 1)]['position']['z']))

                # Calculate object holdings
                # Targets
                dist_tarl = [[0 for x in range(targets_num)] for y in range(gloves_num)]
                dist_tarr = [[0 for x in range(targets_num)] for y in range(gloves_num)]
                # Tables
                dist_tabl = [[0 for x in range(tables_num)] for y in range(gloves_num)]
                dist_tabr = [[0 for x in range(tables_num)] for y in range(gloves_num)]

                # Calculate distance between hands and targets
                for x in range(0, gloves_num):
                    for y in range(0, targets_num):
                        dist_tarl[x][y] = numpy.linalg.norm(handl[x] - target[y])
                        dist_tarr[x][y] = numpy.linalg.norm(handr[x] - target[y])
                        touchtarget = 100

                        # If less than 15cm put in feature vector
                        if dist_tarl[x][y] != 0 and dist_tarl[x][y] < 0.15:
                            touchtarget = y
                        if dist_tarr[x][y] != 0 and dist_tarr[x][y] < 0.15:
                            touchtarget = y

                        if touchtarget != 100:
                            # Put in dictionary
                            feature_dict[second][frame]['P' + str(x + 1) + 'H'] = 'T' + str(y + 1)
                            # Print frame
                            print(feature_dict[second][frame])
                            # Sending messages to teh server
                            my_message = json.dumps(feature_dict[second][frame])
                            my_message = "interpreter;data;" + my_message + "$"
                            # Encode the string to utf-8 and write it to the pipe defined above
                            os.write(pipe_out, my_message.encode("utf-8"))
                            sys.stdout.flush()
                            # Remove from dict
                            feature_dict[second].pop(frame-10, None)
                            touchtarget = 100

                # Calculate distance between hands and tables
                for x in range(0, gloves_num):
                    for y in range(0, tables_num):
                        dist_tabl[x][y] = numpy.linalg.norm(handl[x] - table[y])
                        dist_tabr[x][y] = numpy.linalg.norm(handr[x] - table[y])
                        touchtable = 100

                        # If less than 30cm put in feature vector
                        if dist_tabl[x][y] != 0 and dist_tabl[x][y] < 0.30:
                            touchtable = y
                        if dist_tabr[x][y] != 0 and dist_tabr[x][y] < 0.30:
                            touchtable = y

                        if touchtable != 100:
                            # Put in dictionary
                            feature_dict[second][frame]['P' + str(x + 1) + 'H'] = 'Tab' + str(y + 1)
                            # Print frame
                            print(feature_dict[second][frame])
                            # Sending messages to the server
                            my_message = json.dumps(feature_dict[second][frame])
                            my_message = "interpreter;data;" + my_message + "$"
                            # Encode the string to utf-8 and write it to the pipe defined above
                            os.write(pipe_out, my_message.encode("utf-8"))
                            sys.stdout.flush()
                            # Remove from dict
                            feature_dict[second].pop(frame-10, None)
                            touchtable = 100

                # Gaze Hits
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

            # Get nlp localtime
            nlptime = localtime2

            # First get which second
            second = int(nlptime)

            # Get decimals to decide which frame
            frame = int(math.modf(nlptime)[0] * 50)

            # Put in dictionary
            feature_dict[second][frame]['TS'] = nlpbody['timestamp']
            feature_dict[second][frame]['P1N'] = nlpbody['language']['nouns']
            feature_dict[second][frame]['P1A'] = nlpbody['language']['adjectives']
            feature_dict[second][frame]['P1V'] = nlpbody['language']['verbs']
            feature_dict[second][frame]['P1D'] = nlpbody['language']['determiners']
            feature_dict[second][frame]['P1P'] = nlpbody['language']['pronouns']
            feature_dict[second][frame]['P1F'] = nlpbody['language']['feedback']
            feature_dict[second][frame]['P1ASR'] = nlpbody['speech']

            # Print feature vector
            print(feature_dict[second][frame])
            #zmq_socket.send(msgpack.packb((tobiimocap_dict[second][frame-1], mq.get_shifted_time())))

            # Sending messages to ROS
            my_message = json.dumps(feature_dict[second][frame])
            my_message = "interpreter;data;" + my_message + "$"

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
