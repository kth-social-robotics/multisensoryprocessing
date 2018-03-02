# python feature.py 130.237.67.232 furhat
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
from furhat import connect_to_iristk
from time import sleep

FURHAT_IP = '130.237.67.172' # Furhat IP address
FURHAT_AGENT_NAME = 'system' # Furhat agent name. Can be found under "Connections" in the furhat web-GUI

# Mocap and Furhat Ranges X
MocapMaxx = -1.82
MocapMinx = -3.23
MocapRangex = (MocapMaxx - MocapMinx)
FurhatMaxx = 3
FurhatMinx = -2
FurhatRangex = (FurhatMaxx - FurhatMinx)

# Mocap and Furhat Ranges Y
MocapMaxy = 1.70
MocapMiny = 0.75
MocapRangey = (MocapMaxy - MocapMiny)
FurhatMaxy = 1
FurhatMiny = -1
FurhatRangey = (FurhatMaxy - FurhatMiny)

# Microphones
p1mic = 'mic0'
p2mic = 'mic3'

# Mocap objects
glasses_num = 2
gloves_num = 1
targets_num = 14
tables_num = 1

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
# Time, Frame: Timestamp, P1 Np, P1 Adj, P1 Verb, P1 Det, P1 Pron, P1 Feedback, P1 ASR,
# P2 Np, P2 Adj, P2 Verb, P2 Det, P2 Pron, P2 Feedback, P2 ASR,
# P1 Gaze Label, P2 Gaze Label, P1 Gaze Probabilities, P2 Gaze Probabilities, P2 Holding object, Step
feature_dict[0][0]['TS'] = ''
feature_dict[0][0]['P1N'] = ''
feature_dict[0][0]['P1A'] = ''
feature_dict[0][0]['P1V'] = ''
feature_dict[0][0]['P1D'] = ''
feature_dict[0][0]['P1P'] = ''
feature_dict[0][0]['P1F'] = ''
feature_dict[0][0]['P1ASR'] = ['']
feature_dict[0][0]['P2N'] = ''
feature_dict[0][0]['P2A'] = ''
feature_dict[0][0]['P2V'] = ''
feature_dict[0][0]['P2D'] = ''
feature_dict[0][0]['P2P'] = ''
feature_dict[0][0]['P2F'] = ''
feature_dict[0][0]['P2ASR'] = ['']
feature_dict[0][0]['P1GL'] = ['']
feature_dict[0][0]['P2GL'] = ['']
feature_dict[0][0]['P1GP'] = ['']
feature_dict[0][0]['P2GP'] = ['']
feature_dict[0][0]['P2HL'] = ['']
feature_dict[0][0]['P2PLL'] = ['']
feature_dict[0][0]['P2PLR'] = ['']
feature_dict[0][0]['P2PPL'] = ['']
feature_dict[0][0]['P2PPR'] = ['']
feature_dict[0][0]['S'] = ''

#fixfilter = 0

# Connect to Furhat
with connect_to_iristk(FURHAT_IP) as furhat_client:
    # Introduce Furhat
    furhat_client.say(FURHAT_AGENT_NAME, 'Hello there. I am here to learn how you are putting this furniture together.')
    #sleep(0.01)
    furhat_client.gaze(FURHAT_AGENT_NAME, {'x':3.00,'y':0.00,'z':2.00}) # At default P2 position
    #sleep(0.01)

    # Log Furhat events
    def event_callback(event):
        #print(event) # Receives each event the furhat sends out.
        fd = open('../../../logs/furhat_log.csv','a')
        fd.write(event)
        fd.write('\n')
        fd.close()

    # Listen to events
    furhat_client.start_listening(event_callback) # register the event callback receiver

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
                        if 'mocap_hand' + str(x + 2) + 'l' in mocapbody:
                            handl[x] = numpy.array((mocapbody['mocap_hand' + str(x + 2) + 'l']['position']['x'], mocapbody['mocap_hand' + str(x + 2) + 'l']['position']['y'], mocapbody['mocap_hand' + str(x + 2) + 'l']['position']['z']))
                        if 'mocap_hand' + str(x + 2) + 'r' in mocapbody:
                            handr[x] = numpy.array((mocapbody['mocap_hand' + str(x + 2) + 'r']['position']['x'], mocapbody['mocap_hand' + str(x + 2) + 'r']['position']['y'], mocapbody['mocap_hand' + str(x + 2) + 'r']['position']['z']))
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

                    # Calculate distance between hands and targets
                    for x in range(0, gloves_num):
                        for y in range(0, targets_num):
                            dist_tarl[x][y] = numpy.linalg.norm(handl[x] - target[y])
                            dist_tarr[x][y] = numpy.linalg.norm(handr[x] - target[y])
                            touchtarget = 100

                            # If less than 25cm put in feature vector
                            if dist_tarl[x][y] != 0 and dist_tarl[x][y] < 0.25:
                                touchtarget = y
                            if dist_tarr[x][y] != 0 and dist_tarr[x][y] < 0.25:
                                touchtarget = y

                            if touchtarget != 100:
                                # Put in dictionary
                                feature_dict[second][frame]['TS'] = str(mocaptime)
                                feature_dict[second][frame]['P' + str(x + 1) + 'HL'] = ['T' + str(y + 1)]
                                # Print frame
                                print(feature_dict[second][frame])
                                # Sending messages to the server
                                my_message = json.dumps(feature_dict[second][frame])
                                my_message = "interpreter;data;" + my_message + "$"
                                # Encode the string to utf-8 and write it to the pipe defined above
                                os.write(pipe_out, my_message.encode("utf-8"))
                                sys.stdout.flush()
                                # Remove from dict
                                feature_dict[second].pop(frame, None)
                                touchtarget = 100

                                # Furhat gaze at object holded
                                # Calculate Furhat gaze values based on Mocap object location values
                                MocapValuex = target[y][0]
                                FurhatValuex = (((MocapValuex - MocapMinx) * FurhatRangex) / MocapRangex) + FurhatMinx
                                MocapValuey = target[y][1]
                                FurhatValuey = (((MocapValuey - MocapMiny) * FurhatRangey) / MocapRangey) + FurhatMiny

                                # Check frame and gaze every 10 frames
                                if frame % 10 == 0:
                                    furhat_client.gaze(FURHAT_AGENT_NAME, {'x': FurhatValuex, 'y': FurhatValuey,'z': 2.00})
                                    #sleep(0.001)

                    # aaa

                    # Gaze Hits
                    # Call Matlab script to calculate gaze hits and angles and pointing hits and angles
                    gaze_hits = mateng.gazehits(mocapbody, agent, glasses_num, targets_num, tables_num)
                    # gaze_hits[0] - P1GL
                    # gaze_hits[1] - P2GL
                    # gaze_hits[2] - P1GA
                    # gaze_hits[3] - P2GA
                    # gaze_hits[4] - P2PLL
                    # gaze_hits[5] - P2PRL
                    # gaze_hits[6] - P2PLA
                    # gaze_hits[7] - P2PRA

                    # Gaze on Yumi Table
                    if agent == 'yumi':
                        # Vision system point bottom right: x = 0.65, y = 0.34
                        # Mocap system point bottom right: x = -2.81, z = 4.19
                        # xrobot = -zmocap (-3.54)
                        # yrobot = -xmocap (+3.15)

                        # Table Tobii 1 gaze position
                        if gaze_hits[0] == 'Tab1':
                            xrobot = 0.65 - (gaze_hits[1][0][0] - 4.19) # xrobot - (xcurrent - xmocap)
                            yrobot = 0.34 - (gaze_hits[1][0][2] + 2.81) # yrobot - (ycurrent + ymocap)

                            # Put in dictionary
                            feature_dict[second][frame]['P1GP'] = [xrobot, yrobot]

                            # Print frame
                            print(feature_dict[second][frame])

                            # Sending messages to ROS
                            my_message = json.dumps(feature_dict[second][frame])
                            my_message = "interpreter;data;" + my_message + "$"

                            # Encode the string to utf-8 and write it to the pipe defined above
                            os.write(pipe_out, my_message.encode("utf-8"))
                            sys.stdout.flush()

                            # Remove from dict
                            feature_dict[second].pop(frame, None)

                    # Glasses 1 Gaze Label
                    if gaze_hits[0] != ['']:
                        # Put in dictionary
                        feature_dict[second][frame]['TS'] = str(mocaptime)
                        feature_dict[second][frame]['P1GL'] = [gaze_hits[0]]

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

                        # Sending messages to the server
                        my_message = json.dumps(feature_dict[second][frame])
                        my_message = "interpreter;data;" + my_message + "$"
                        # Encode the string to utf-8 and write it to the pipe defined above
                        os.write(pipe_out, my_message.encode("utf-8"))
                        sys.stdout.flush()

                        # Remove from dict
                        feature_dict[second].pop(frame, None)

                    # Glasses 2 Gaze Label
                    if gaze_hits[1] != ['']:
                        # Put in dictionary
                        feature_dict[second][frame]['TS'] = str(mocaptime)
                        feature_dict[second][frame]['P2GL'] = [gaze_hits[1]]

                        # Print frame
                        print(feature_dict[second][frame])

                        # Sending messages to the server
                        my_message = json.dumps(feature_dict[second][frame])
                        my_message = "interpreter;data;" + my_message + "$"
                        # Encode the string to utf-8 and write it to the pipe defined above
                        os.write(pipe_out, my_message.encode("utf-8"))
                        sys.stdout.flush()

                        # Remove from dict
                        feature_dict[second].pop(frame, None)

                    # Hand Left 2 Point Label
                    if gaze_hits[4] != ['']:
                        # Put in dictionary
                        feature_dict[second][frame]['TS'] = str(mocaptime)
                        feature_dict[second][frame]['P2PLL'] = [gaze_hits[4]]

                        # Print frame
                        print(feature_dict[second][frame])

                        # Sending messages to the server
                        my_message = json.dumps(feature_dict[second][frame])
                        my_message = "interpreter;data;" + my_message + "$"
                        # Encode the string to utf-8 and write it to the pipe defined above
                        os.write(pipe_out, my_message.encode("utf-8"))
                        sys.stdout.flush()

                        # Remove from dict
                        feature_dict[second].pop(frame, None)

                    # Hand Right 2 Point Label
                    if gaze_hits[5] != ['']:
                        # Put in dictionary
                        feature_dict[second][frame]['TS'] = str(mocaptime)
                        feature_dict[second][frame]['P2PLR'] = [gaze_hits[5]]

                        # Print frame
                        print(feature_dict[second][frame])

                        # Sending messages to the server
                        my_message = json.dumps(feature_dict[second][frame])
                        my_message = "interpreter;data;" + my_message + "$"
                        # Encode the string to utf-8 and write it to the pipe defined above
                        os.write(pipe_out, my_message.encode("utf-8"))
                        sys.stdout.flush()

                        # Remove from dict
                        feature_dict[second].pop(frame, None)

                    # Glasses 1 and 2 Gaze Angles (Probabilities)
                    np1 = numpy.array(gaze_hits[2])
                    np2 = numpy.array(gaze_hits[3])
                    # Put in dictionary
                    feature_dict[second][frame]['TS'] = str(mocaptime)
                    feature_dict[second][frame]['P1GP'] = [np1.tolist()]
                    feature_dict[second][frame]['P2GP'] = [np2.tolist()]

                    # Hands L and R Pointing Angles (Probabilities)
                    np3 = numpy.array(gaze_hits[6])
                    np4 = numpy.array(gaze_hits[7])
                    # Put in dictionary
                    feature_dict[second][frame]['TS'] = str(mocaptime)
                    feature_dict[second][frame]['P2PPL'] = [np3.tolist()]
                    feature_dict[second][frame]['P2PPR'] = [np4.tolist()]

                    # Print frame
                    #print(feature_dict[second][frame])

                    # Sending messages to the server
                    my_message = json.dumps(feature_dict[second][frame])
                    my_message = "interpreter;data;" + my_message + "$"
                    # Encode the string to utf-8 and write it to the pipe defined above
                    os.write(pipe_out, my_message.encode("utf-8"))
                    sys.stdout.flush()

                    # Remove from dict
                    feature_dict[second].pop(frame, None)

                    # aaa

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
                if nlpbody['mic'] == p1mic:
                    feature_dict[second][frame]['TS'] = str(nlpbody['timestamp'])
                    feature_dict[second][frame]['P1N'] = nlpbody['language']['nouns']
                    feature_dict[second][frame]['P1A'] = nlpbody['language']['adjectives']
                    feature_dict[second][frame]['P1V'] = nlpbody['language']['verbs']
                    feature_dict[second][frame]['P1D'] = nlpbody['language']['determiners']
                    feature_dict[second][frame]['P1P'] = nlpbody['language']['pronouns']
                    feature_dict[second][frame]['P1F'] = nlpbody['language']['feedback']
                    feature_dict[second][frame]['P1ASR'] = [nlpbody['speech']]
                elif nlpbody['mic'] == p2mic:
                    feature_dict[second][frame]['TS'] = str(nlpbody['timestamp'])
                    feature_dict[second][frame]['P2N'] = nlpbody['language']['nouns']
                    feature_dict[second][frame]['P2A'] = nlpbody['language']['adjectives']
                    feature_dict[second][frame]['P2V'] = nlpbody['language']['verbs']
                    feature_dict[second][frame]['P2D'] = nlpbody['language']['determiners']
                    feature_dict[second][frame]['P2P'] = nlpbody['language']['pronouns']
                    feature_dict[second][frame]['P2F'] = nlpbody['language']['feedback']
                    feature_dict[second][frame]['P2ASR'] = [nlpbody['speech']]

                # Furhat react to P1 speech
                if nlpbody['mic'] == p1mic and nlpbody['speech'] == 'hello ':
                    furhat_client.say(FURHAT_AGENT_NAME, 'Hi.')
                    #sleep(0.01)

                # Furhat look at person speaking
                if nlpbody['mic'] == p1mic:
                    furhat_client.gaze(FURHAT_AGENT_NAME, {'x':-2.00,'y':0.00,'z':2.00}) # At default P1 position
                elif nlpbody['mic'] == p2mic:
                    furhat_client.gaze(FURHAT_AGENT_NAME, {'x':3.00,'y':0.00,'z':2.00}) # At default P2 position

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
                feature_dict[second].pop(frame, None)

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
