# python feature.py 130.237.67.190 furhat
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
import csv

# Print messages
DEBUG = False

FURHAT_IP = '130.237.67.115' # Furhat IP address
FURHAT_AGENT_NAME = 'system' # Furhat agent name. Can be found under "Connections" in the furhat web-GUI

# Microphones
p1mic = 'mic9'
p2mic = 'mic3'

# Mocap objects
glasses_num = 2
gloves_num = 2
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
#mateng.addpath(r'/Users/diko/Dropbox/University/PhD/Code/MultiSensoryProcessing/multisensoryprocessing/matlab', nargout=0)
mateng.addpath(r'/Users/tmhadmin/Documents/GitHub/multisensoryprocessing/matlab', nargout=0)
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
# Time, Frame: Timestamp,
# P1 Np, P1 Adj, P1 Verb, P1 Det, P1 Pron, P1 Feedback, P1 ASR, P1 Keywords,
# P2 Np, P2 Adj, P2 Verb, P2 Det, P2 Pron, P2 Feedback, P2 ASR, P2 Keywords,
# P1 Gaze Label, P2 Gaze Label, P1 Gaze Probabilities, P2 Gaze Probabilities,
# P1 Holding object, P2 Holding object,
# P1 Pointing Label, P1 Pointing Probability Left, P1 Pointing Probability Right,
# P2 Pointing Label, P2 Pointing Probability Left, P2 Pointing Probability Right,
# P1 Head Label, P1 Head Probability,
# P2 Head Label, P2 Head Probability,
# Step
feature_dict[0][0]['TS'] = ''
feature_dict[0][0]['P1N'] = ''
feature_dict[0][0]['P1A'] = ''
feature_dict[0][0]['P1V'] = ''
feature_dict[0][0]['P1D'] = ''
feature_dict[0][0]['P1P'] = ''
feature_dict[0][0]['P1F'] = ''
feature_dict[0][0]['P1ASR'] = ['']
feature_dict[0][0]['P1Keywords'] = ['']
feature_dict[0][0]['P2N'] = ''
feature_dict[0][0]['P2A'] = ''
feature_dict[0][0]['P2V'] = ''
feature_dict[0][0]['P2D'] = ''
feature_dict[0][0]['P2P'] = ''
feature_dict[0][0]['P2F'] = ''
feature_dict[0][0]['P2ASR'] = ['']
feature_dict[0][0]['P2Keywords'] = ['']
feature_dict[0][0]['P1GL'] = ['']
feature_dict[0][0]['P2GL'] = ['']
feature_dict[0][0]['P1GP'] = ['']
feature_dict[0][0]['P2GP'] = ['']
feature_dict[0][0]['P1HL'] = ['']
feature_dict[0][0]['P2HL'] = ['']
feature_dict[0][0]['P1PL'] = ['']
feature_dict[0][0]['P1PPL'] = ['']
feature_dict[0][0]['P1PPR'] = ['']
feature_dict[0][0]['P2PL'] = ['']
feature_dict[0][0]['P2PPL'] = ['']
feature_dict[0][0]['P2PPR'] = ['']
feature_dict[0][0]['P1HDL'] = ['']
feature_dict[0][0]['P1HDP'] = ['']
feature_dict[0][0]['P2HDL'] = ['']
feature_dict[0][0]['P2HDP'] = ['']
feature_dict[0][0]['S'] = ''

# Save to log file
with open('../../../logs/probabilities.csv', 'wb') as f:  # Just use 'w' mode in 3.x
    w = csv.DictWriter(f, feature_dict[0][0].keys(), delimiter=";")
    w.writeheader()

    # Connect to Furhat
    with connect_to_iristk(FURHAT_IP) as furhat_client:
        # Introduce Furhat
        furhat_client.say(FURHAT_AGENT_NAME, 'It seems like I can now hear what you are saying.')
        #furhat_client.gaze(FURHAT_AGENT_NAME, {'x':3.00,'y':0.00,'z':2.00}) # At default P1 position
        furhat_client.gaze(FURHAT_AGENT_NAME, {'x':-2.00,'y':0.00,'z':2.00}) # At default P2 position

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
                                    feature_dict[second][frame]['TS'] = str(mocaptime)
                                    feature_dict[second][frame]['P' + str(x + 1) + 'HL'] = ['T' + str(y + 1)]
                                    # Print frame
                                    if DEBUG: print(feature_dict[second][frame])
                                    # Sending messages to the server
                                    my_message = json.dumps(feature_dict[second][frame])
                                    my_message = "interpreter;data;" + my_message + "$"
                                    # Encode the string to utf-8 and write it to the pipe defined above
                                    os.write(pipe_out, my_message.encode("utf-8"))
                                    sys.stdout.flush()
                                    # Remove from dict
                                    #feature_dict[second].pop(frame, None)
                                    touchtarget = 100

                                    # Furhat gaze at object holded apart form the 3 big ones
                                    # Furhat and object positions
                                    if y != 0 and y != 1 and y != 2:
                                        fx = mocapbody['mocap_furhat']['position']['x']
                                        fy = mocapbody['mocap_furhat']['position']['y']
                                        fz = mocapbody['mocap_furhat']['position']['z']
                                        ox = mocapbody['mocap_target' + str(y + 1)]['position']['x']
                                        oy = mocapbody['mocap_target' + str(y + 1)]['position']['y']
                                        oz = mocapbody['mocap_target' + str(y + 1)]['position']['z']
                                        furhat_gaze_target_x = oz - fz
                                        furhat_gaze_target_y = oy - fy
                                        furhat_gaze_target_z = - (ox - fx)

                                        # Make sure the position is in furhat's limits
                                        furhat_xlimit = False
                                        furhat_ylimit = False
                                        furhat_zlimit = False
                                        if -4 <= furhat_gaze_target_x <= 4:
                                            furhat_xlimit = True
                                        if -1 <= furhat_gaze_target_y <= 1:
                                            furhat_ylimit = True
                                        if 0 <= furhat_gaze_target_z <= 3:
                                            furhat_zlimit = True

                                        # Move only every 10 frames and if gaze is within the limits
                                        if frame % 10 == 0 and furhat_xlimit and furhat_ylimit and furhat_zlimit:
                                            furhat_client.gaze(FURHAT_AGENT_NAME, {'x': furhat_gaze_target_x, 'y': furhat_gaze_target_y,'z': furhat_gaze_target_z})

                        # Gaze, Head and Pointing Hits
                        # Call Matlab script to calculate gaze, head and pointing hits and angles
                        gaze_hits = mateng.gazehits(mocapbody, agent, glasses_num, gloves_num, targets_num, tables_num)
                        # gaze_hits[0] - P1GL
                        # gaze_hits[1] - P2GL
                        # gaze_hits[2] - P1GA
                        # gaze_hits[3] - P2GA
                        # gaze_hits[4] - P1PL
                        # gaze_hits[5] - P1PLA
                        # gaze_hits[6] - P1PRA
                        # gaze_hits[7] - P2PL
                        # gaze_hits[8] - P2PLA
                        # gaze_hits[9] - P2PRA
                        # gaze_hits[10] - P1HL
                        # gaze_hits[11] - P2HL
                        # gaze_hits[12] - P1HA
                        # gaze_hits[13] - P2HA

                        # # Gaze on Yumi Table
                        # if agent == 'yumi':
                        #     # Vision system point bottom right: x = 0.65, y = 0.34
                        #     # Mocap system point bottom right: x = -2.81, z = 4.19
                        #     # xrobot = -zmocap (-3.54)
                        #     # yrobot = -xmocap (+3.15)
                        #
                        #     # Table Tobii 1 gaze position
                        #     if gaze_hits[0] == 'Tab1':
                        #         xrobot = 0.65 - (gaze_hits[1][0][0] - 4.19) # xrobot - (xcurrent - xmocap)
                        #         yrobot = 0.34 - (gaze_hits[1][0][2] + 2.81) # yrobot - (ycurrent + ymocap)
                        #
                        #         # Put in dictionary
                        #         feature_dict[second][frame]['P1GP'] = [xrobot, yrobot]
                        #
                        #         # Print frame
                        #         #print(feature_dict[second][frame])
                        #
                        #         # Sending messages to ROS
                        #         my_message = json.dumps(feature_dict[second][frame])
                        #         my_message = "interpreter;data;" + my_message + "$"
                        #
                        #         # Encode the string to utf-8 and write it to the pipe defined above
                        #         os.write(pipe_out, my_message.encode("utf-8"))
                        #         sys.stdout.flush()
                        #
                        #         # Remove from dict
                        #         feature_dict[second].pop(frame, None)

                        # Glasses 1 Gaze Label
                        if gaze_hits[0] != ['']:
                            # Put in dictionary
                            feature_dict[second][frame]['TS'] = str(mocaptime)
                            feature_dict[second][frame]['P1GL'] = [gaze_hits[0]]

                            # Print frame
                            if DEBUG: print(feature_dict[second][frame])

                            # Print for calibration
                            if gaze_hits[0] == 'Calibration':
                                print('P1 - Calibration')

                            # Furhat look at P1 if looking at Furhat
                            if gaze_hits[0] == 'Furhat':
                                furhat_client.gaze(FURHAT_AGENT_NAME, {'x':3.00,'y':0.00,'z':2.00}) # At default P1 position

                            # Sending messages to the server
                            my_message = json.dumps(feature_dict[second][frame])
                            my_message = "interpreter;data;" + my_message + "$"
                            # Encode the string to utf-8 and write it to the pipe defined above
                            os.write(pipe_out, my_message.encode("utf-8"))
                            sys.stdout.flush()

                            # Remove from dict
                            #feature_dict[second].pop(frame, None)

                        # Glasses 2 Gaze Label
                        if gaze_hits[1] != ['']:
                            # Put in dictionary
                            feature_dict[second][frame]['TS'] = str(mocaptime)
                            feature_dict[second][frame]['P2GL'] = [gaze_hits[1]]

                            # Print frame
                            if DEBUG: print(feature_dict[second][frame])

                            # Print for calibration
                            if gaze_hits[1] == 'Calibration':
                                print('P2 - Calibration')

                            # Furhat look at P2 if looking at Furhat
                            if gaze_hits[1] == 'Furhat':
                                furhat_client.gaze(FURHAT_AGENT_NAME, {'x':-2.00,'y':0.00,'z':2.00}) # At default P2 position

                            # Sending messages to the server
                            my_message = json.dumps(feature_dict[second][frame])
                            my_message = "interpreter;data;" + my_message + "$"
                            # Encode the string to utf-8 and write it to the pipe defined above
                            os.write(pipe_out, my_message.encode("utf-8"))
                            sys.stdout.flush()

                            # Remove from dict
                            #feature_dict[second].pop(frame, None)

                        # Furhat follow object of joint attention
                        if gaze_hits[0] != [''] and gaze_hits[1] != [''] and gaze_hits[0] == gaze_hits[1]:
                            # Check that it is only the objects
                            if gaze_hits[0] != 'Screen' and gaze_hits[0] != 'Furhat' and gaze_hits[0] != 'Calibration':
                                # Furhat and object positions
                                fx = mocapbody['mocap_furhat']['position']['x']
                                fy = mocapbody['mocap_furhat']['position']['y']
                                fz = mocapbody['mocap_furhat']['position']['z']
                                ox = mocapbody['mocap_target' + gaze_hits[0][1:]]['position']['x']
                                oy = mocapbody['mocap_target' + gaze_hits[0][1:]]['position']['y']
                                oz = mocapbody['mocap_target' + gaze_hits[0][1:]]['position']['z']
                                furhat_gaze_target_x = oz - fz
                                furhat_gaze_target_y = oy - fy
                                furhat_gaze_target_z = - (ox - fx)

                                # Make sure the position is in furhat's limits
                                furhat_xlimit = False
                                furhat_ylimit = False
                                furhat_zlimit = False
                                if -4 <= furhat_gaze_target_x <= 4:
                                    furhat_xlimit = True
                                if -1 <= furhat_gaze_target_y <= 1:
                                    furhat_ylimit = True
                                if 0 <= furhat_gaze_target_z <= 3:
                                    furhat_zlimit = True

                                # Move only every 10 frames and if gaze is within the limits
                                if frame % 10 == 0 and furhat_xlimit and furhat_ylimit and furhat_zlimit:
                                    furhat_client.gaze(FURHAT_AGENT_NAME, {'x': furhat_gaze_target_x, 'y': furhat_gaze_target_y,'z': furhat_gaze_target_z})

                        # Hands 1 Point Label
                        if gaze_hits[4] != ['']:
                            # Put in dictionary
                            feature_dict[second][frame]['TS'] = str(mocaptime)
                            feature_dict[second][frame]['P1PL'] = [gaze_hits[4]]

                            # Print frame
                            if DEBUG: print(feature_dict[second][frame])

                            # Sending messages to the server
                            my_message = json.dumps(feature_dict[second][frame])
                            my_message = "interpreter;data;" + my_message + "$"
                            # Encode the string to utf-8 and write it to the pipe defined above
                            os.write(pipe_out, my_message.encode("utf-8"))
                            sys.stdout.flush()

                            # Remove from dict
                            #feature_dict[second].pop(frame, None)

                        # Hands 2 Point Label
                        if gaze_hits[7] != ['']:
                            # Put in dictionary
                            feature_dict[second][frame]['TS'] = str(mocaptime)
                            feature_dict[second][frame]['P2LL'] = [gaze_hits[7]]

                            # Print frame
                            if DEBUG: print(feature_dict[second][frame])

                            # Sending messages to the server
                            my_message = json.dumps(feature_dict[second][frame])
                            my_message = "interpreter;data;" + my_message + "$"
                            # Encode the string to utf-8 and write it to the pipe defined above
                            os.write(pipe_out, my_message.encode("utf-8"))
                            sys.stdout.flush()

                            # Remove from dict
                            #feature_dict[second].pop(frame, None)

                        # Head 1 Point Label
                        if gaze_hits[10] != ['']:
                            # Put in dictionary
                            feature_dict[second][frame]['TS'] = str(mocaptime)
                            feature_dict[second][frame]['P1HDL'] = [gaze_hits[10]]

                            # Print frame
                            if DEBUG: print(feature_dict[second][frame])

                            # Sending messages to the server
                            my_message = json.dumps(feature_dict[second][frame])
                            my_message = "interpreter;data;" + my_message + "$"
                            # Encode the string to utf-8 and write it to the pipe defined above
                            os.write(pipe_out, my_message.encode("utf-8"))
                            sys.stdout.flush()

                            # Remove from dict
                            #feature_dict[second].pop(frame, None)

                        # Head 2 Point Label
                        if gaze_hits[11] != ['']:
                            # Put in dictionary
                            feature_dict[second][frame]['TS'] = str(mocaptime)
                            feature_dict[second][frame]['P2HDL'] = [gaze_hits[11]]

                            # Print frame
                            if DEBUG: print(feature_dict[second][frame])

                            # Sending messages to the server
                            my_message = json.dumps(feature_dict[second][frame])
                            my_message = "interpreter;data;" + my_message + "$"
                            # Encode the string to utf-8 and write it to the pipe defined above
                            os.write(pipe_out, my_message.encode("utf-8"))
                            sys.stdout.flush()

                            # Remove from dict
                            #feature_dict[second].pop(frame, None)

                        # Glasses 1 and 2 Gaze Angles (Probabilities)
                        np1 = numpy.array(gaze_hits[2])
                        np2 = numpy.array(gaze_hits[3])
                        # Put in dictionary
                        feature_dict[second][frame]['TS'] = str(mocaptime)
                        feature_dict[second][frame]['P1GP'] = [np1.tolist()]
                        feature_dict[second][frame]['P2GP'] = [np2.tolist()]

                        # Hands 1L,1R and 2L,2R Pointing Angles (Probabilities)
                        np3 = numpy.array(gaze_hits[5])
                        np4 = numpy.array(gaze_hits[6])
                        np5 = numpy.array(gaze_hits[8])
                        np6 = numpy.array(gaze_hits[9])
                        # Put in dictionary
                        feature_dict[second][frame]['TS'] = str(mocaptime)
                        feature_dict[second][frame]['P1PPL'] = [np3.tolist()]
                        feature_dict[second][frame]['P1PPR'] = [np4.tolist()]
                        feature_dict[second][frame]['P2PPL'] = [np5.tolist()]
                        feature_dict[second][frame]['P2PPR'] = [np6.tolist()]

                        # Glasses 1 and 2 Head Angles (Probabilities)
                        np7 = numpy.array(gaze_hits[12])
                        np8 = numpy.array(gaze_hits[13])
                        # Put in dictionary
                        feature_dict[second][frame]['TS'] = str(mocaptime)
                        feature_dict[second][frame]['P1HDP'] = [np7.tolist()]
                        feature_dict[second][frame]['P2HDP'] = [np8.tolist()]

                        # Print frame
                        #print(feature_dict[second][frame])

                        # Sending messages to the server
                        #my_message = json.dumps(feature_dict[second][frame])
                        #my_message = "interpreter;data;" + my_message + "$"
                        # Encode the string to utf-8 and write it to the pipe defined above
                        #os.write(pipe_out, my_message.encode("utf-8"))
                        #sys.stdout.flush()

                        # Log to csv file
                        w.writerow(feature_dict[second][frame])

                        # Remove from dict (all features - also nlp)
                        feature_dict[second].pop(frame, None)

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
                        feature_dict[second][frame]['P1Keywords'] = [nlpbody['keywords']]
                    elif nlpbody['mic'] == p2mic:
                        feature_dict[second][frame]['TS'] = str(nlpbody['timestamp'])
                        feature_dict[second][frame]['P2N'] = nlpbody['language']['nouns']
                        feature_dict[second][frame]['P2A'] = nlpbody['language']['adjectives']
                        feature_dict[second][frame]['P2V'] = nlpbody['language']['verbs']
                        feature_dict[second][frame]['P2D'] = nlpbody['language']['determiners']
                        feature_dict[second][frame]['P2P'] = nlpbody['language']['pronouns']
                        feature_dict[second][frame]['P2F'] = nlpbody['language']['feedback']
                        feature_dict[second][frame]['P2ASR'] = [nlpbody['speech']]
                        feature_dict[second][frame]['P2Keywords'] = [nlpbody['keywords']]

                    # Furhat react to P1 speech
                    if nlpbody['mic'] == p1mic and nlpbody['speech'] == 'hello ':
                        furhat_client.gaze(FURHAT_AGENT_NAME, {'x':3.00,'y':0.00,'z':2.00}) # At default P1 position
                        furhat_client.say(FURHAT_AGENT_NAME, 'Hi.')

                    # Furhat react to P2 speech
                    if nlpbody['mic'] == p2mic and nlpbody['speech'] == 'hello ':
                        furhat_client.gaze(FURHAT_AGENT_NAME, {'x':-2.00,'y':0.00,'z':2.00}) # At default P2 position
                        furhat_client.say(FURHAT_AGENT_NAME, 'Hi.')

                    # Furhat look at person speaking
                    # if nlpbody['mic'] == p1mic:
                    #     furhat_client.gaze(FURHAT_AGENT_NAME, {'x':3.00,'y':0.00,'z':2.00}) # At default P1 position
                    # elif nlpbody['mic'] == p2mic:
                    #     furhat_client.gaze(FURHAT_AGENT_NAME, {'x':-2.00,'y':0.00,'z':2.00}) # At default P2 position

                    # Print feature vector
                    print(feature_dict[second][frame])
                    #zmq_socket.send(msgpack.packb((tobiimocap_dict[second][frame-1], mq.get_shifted_time())))

                    # Sending messages to attention module
                    my_message = json.dumps(feature_dict[second][frame])
                    my_message = "interpreter;data;" + my_message + "$"

                    # Encode the string to utf-8 and write it to the pipe defined above
                    os.write(pipe_out, my_message.encode("utf-8"))
                    sys.stdout.flush()

                    # Remove value from dict
                    #feature_dict[second].pop(frame, None)

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
