# python2 feature.py
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
import time, os, fnmatch, shutil

# Print messages
DEBUG = False

# Microphones
p1mic = 'mic2'

# Mocap objects
glasses_num = 1
gloves_num = 1
targets_num = 1
tables_num = 1

# Start matlab engine
mateng = matlab.engine.start_matlab()
mateng.addpath(r'/Users/diko/Dropbox/University/PhD/Code/MultiSensoryProcessing/multisensoryprocessing/matlab', nargout=0)
#mateng.addpath(r'C:/Users/PMIL/Documents/GitHub/multisensoryprocessing/matlab', nargout=0)
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
# P1 ASR, P1 Keywords,
# P1 Gaze Label,
# P1 Gaze Probabilities,
# P1 Holding object,
# P1 Pointing Label, P1 Pointing Probability Left, P1 Pointing Probability Right,
# P1 Head Label, P1 Head Probability,
# P1 Pupil Size Left, P1 Pupil Size Right,
# Step

feature_dict[0][0]['TS'] = ''
feature_dict[0][0]['P1ASR'] = ['']
feature_dict[0][0]['P1Keywords'] = ['']
feature_dict[0][0]['P1GL'] = ['']
feature_dict[0][0]['P1GP'] = ['']
feature_dict[0][0]['P1HL'] = ['']
feature_dict[0][0]['P1PL'] = ['']
feature_dict[0][0]['P1PPL'] = ['']
feature_dict[0][0]['P1PPR'] = ['']
feature_dict[0][0]['P1HDL'] = ['']
feature_dict[0][0]['P1HDP'] = ['']
feature_dict[0][0]['P1PSL'] = ['']
feature_dict[0][0]['P1PSR'] = ['']
feature_dict[0][0]['S'] = ''

# Save to log file
logt = time.localtime()
logtimestamp = time.strftime('%b-%d-%Y_%H%M', logt)
with open('../../../logs/experiment2/recs/rec_' + logtimestamp + ".csv", 'wb') as f:  # Just use 'w' mode in 3.x
    w = csv.DictWriter(f, feature_dict[0][0].keys(), delimiter=";")
    w.writeheader()

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
                    furhat = []
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
                    # Furhat
                    furhat.append(0)

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
                    # Furhat
                    if 'mocap_furhat' in mocapbody:
                        furhat[0] = numpy.array((mocapbody['mocap_furhat']['position']['x'], mocapbody['mocap_furhat']['position']['y'], mocapbody['mocap_furhat']['position']['z']))

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
                                touchtarget = 100

                    # Gaze, Head and Pointing Hits
                    # Call Matlab script to calculate gaze, head and pointing hits and angles
                    gaze_hits = mateng.gazehits(mocapbody, targets_num)
                    # gaze_hits[0] - P1GL
                    # gaze_hits[3] - P1GA
                    # gaze_hits[6] - P1PL
                    # gaze_hits[7] - P1PLA
                    # gaze_hits[8] - P1PRA
                    # gaze_hits[12] - P1HL
                    # gaze_hits[15] - P1HA

                    # Get pupil size and save to dict
                    if 'tobii_glasses1' in mocapbody:
                        pdleft = mocapbody['tobii_glasses1']['pdleft']
                        pdright = mocapbody['tobii_glasses1']['pdright']

                        # Put in dictionary
                        feature_dict[second][frame]['TS'] = str(mocaptime)
                        feature_dict[second][frame]['P1PSL'] = [pdleft]
                        feature_dict[second][frame]['P1PSR'] = [pdright]

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

                    # Hands 1 Point Label
                    if gaze_hits[6] != ['']:
                        # Put in dictionary
                        feature_dict[second][frame]['TS'] = str(mocaptime)
                        feature_dict[second][frame]['P1PL'] = [gaze_hits[6]]

                        # Print frame
                        if DEBUG: print(feature_dict[second][frame])

                    # Head 1 Point Label
                    if gaze_hits[12] != ['']:
                        # Put in dictionary
                        feature_dict[second][frame]['TS'] = str(mocaptime)
                        feature_dict[second][frame]['P1HDL'] = [gaze_hits[12]]

                        # Print frame
                        if DEBUG: print(feature_dict[second][frame])

                    # Glasses 1 Gaze Angles (Probabilities)
                    np1 = numpy.array(gaze_hits[3])

                    # Put in dictionary
                    feature_dict[second][frame]['TS'] = str(mocaptime)
                    feature_dict[second][frame]['P1GP'] = [np1.tolist()]

                    # Hands 1L,1R Pointing Angles (Probabilities)
                    np4 = numpy.array(gaze_hits[7])
                    np5 = numpy.array(gaze_hits[8])

                    # Put in dictionary
                    feature_dict[second][frame]['P1PPL'] = [np4.tolist()]
                    feature_dict[second][frame]['P1PPR'] = [np5.tolist()]

                    # Glasses 1 Head Angles (Probabilities)
                    np8 = numpy.array(gaze_hits[15])

                    # Put in dictionary
                    feature_dict[second][frame]['P1HDP'] = [np8.tolist()]

                    # Send frame
                    #print(feature_dict[second][frame])
                    zmq_socket.send(msgpack.packb((feature_dict[second][frame], mq.get_shifted_time())))

                    # Log to csv file
                    w.writerow(feature_dict[second][frame])

                    # Remove from dict (all features - also nlp)
                    feature_dict[second-5].pop(frame, None)

        t1 = Thread(target = runA)
        t1.setDaemon(True)
        t1.start()

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
                    feature_dict[second][frame]['P1ASR'] = [nlpbody['speech']]
                    feature_dict[second][frame]['P1Keywords'] = [nlpbody['keywords']]

                # Print feature vector
                print(feature_dict[second][frame])

        t2 = Thread(target = runB)
        t2.setDaemon(True)
        t2.start()

    mq = MessageQueue('feature-processor')
    mq.bind_queue(exchange='processor', routing_key=settings['messaging']['mocaptobii_processing'], callback=mocapcallback)
    mq.bind_queue(exchange='processor', routing_key=settings['messaging']['nlp_data'], callback=nlpcallback)

    mq.listen()

    zmq_socket.send(b'CLOSE')
    zmq_socket.close()
