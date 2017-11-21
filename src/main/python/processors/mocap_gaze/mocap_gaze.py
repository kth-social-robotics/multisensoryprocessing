# Get access to tobii live video streaming: rtsp://130.237.67.195:8554/live/eyes or scene
# websocketd --port=8080 python mocap_gaze.py

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

# Start matlab engine
mateng = matlab.engine.start_matlab()
mateng.addpath(r'/Users/diko/Dropbox/University/PhD/Code/MultiSensoryProcessing/multisensoryprocessing/src/main/python/processors/mocap_gaze/matlab', nargout=0)
print("MATLAB")

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Define server
zmq_socket, zmq_server_addr = create_zmq_server()
mq = MessageQueue('mocaptobii-processor')

mq.publish(
    exchange='processor',
    routing_key=settings['messaging']['mocaptobii_processing'],
    body={'address': zmq_server_addr, 'file_type': 'txt'}
)

# Dictionaries
tobiimocap_dict = defaultdict(lambda : defaultdict(dict))

# Each key is the local timestamp in seconds. The second key is the frame
tobiimocap_dict[0][0]['device'] = 'body'

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
            mocaptime = mocapbody['localtime']

            # First get which second
            second = int(mocaptime)

            # Get decimals to decide which frame
            frame = int(math.modf(mocaptime)[0] * 50)

            # Put in dictionary
            tobiimocap_dict[second][frame]['mocap_' + mocapbody['name']] = mocapbody

            # Get gaze values from the previous frame
            if 'tobii_glasses1' in tobiimocap_dict[second][frame-1]:
                # Get values from json
                gp3 = matlab.double([tobiimocap_dict[second][frame-1]['tobii_glasses1']['gp3']['x'], tobiimocap_dict[second][frame-1]['tobii_glasses1']['gp3']['y'], tobiimocap_dict[second][frame-1]['tobii_glasses1']['gp3']['z']])
                pos = matlab.double([tobiimocap_dict[second][frame-1]['mocap_glasses1']['position']['x'], tobiimocap_dict[second][frame-1]['mocap_glasses1']['position']['y'], tobiimocap_dict[second][frame-1]['mocap_glasses1']['position']['z']])
                quat = matlab.double([tobiimocap_dict[second][frame-1]['mocap_glasses1']['rotation']['x'], tobiimocap_dict[second][frame-1]['mocap_glasses1']['rotation']['y'], tobiimocap_dict[second][frame-1]['mocap_glasses1']['rotation']['z'], tobiimocap_dict[second][frame-1]['mocap_glasses1']['rotation']['w']])
                rgbMarkers = matlab.double([[[tobiimocap_dict[second][frame-1]['mocap_glasses1']['marker1']['x'], tobiimocap_dict[second][frame-1]['mocap_glasses1']['marker2']['x'], tobiimocap_dict[second][frame-1]['mocap_glasses1']['marker3']['x'], tobiimocap_dict[second][frame-1]['mocap_glasses1']['marker4']['x']], [tobiimocap_dict[second][frame-1]['mocap_glasses1']['marker1']['y'], tobiimocap_dict[second][frame-1]['mocap_glasses1']['marker2']['y'], tobiimocap_dict[second][frame-1]['mocap_glasses1']['marker3']['y'], tobiimocap_dict[second][frame-1]['mocap_glasses1']['marker4']['y']], [tobiimocap_dict[second][frame-1]['mocap_glasses1']['marker1']['z'], tobiimocap_dict[second][frame-1]['mocap_glasses1']['marker2']['z'], tobiimocap_dict[second][frame-1]['mocap_glasses1']['marker3']['z'], tobiimocap_dict[second][frame-1]['mocap_glasses1']['marker4']['z']]]]) # [x1, x2, x3], [y1, y2, y3], [z1, z2, z3]

                # Combine mocap and gaze. GP3 in mocap space (in Matlab)
                gp3_3d = mateng.python(gp3, pos, quat, rgbMarkers)

                # Get 3d values
                gaze_left = {"x": gp3_3d[0][0][0], "y": gp3_3d[0][1][0], "z": gp3_3d[0][2][0]}
                gaze_right = {"x": gp3_3d[0][0][1], "y": gp3_3d[0][1][1], "z": gp3_3d[0][2][1]}
                gaze_gp3 = {"x": gp3_3d[0][0][2], "y": gp3_3d[0][1][2], "z": gp3_3d[0][2][2]}
                head_pose = {"x": gp3_3d[0][0][3], "y": gp3_3d[0][1][3], "z": gp3_3d[0][2][3]}

                # Update dict values
                tobiimocap_dict[second][frame-1]['tobii_glasses1']['gp3_3d'] = gaze_gp3
                tobiimocap_dict[second][frame-1]['tobii_glasses1']['headpose'] = head_pose

            # Print 1 frame before
            print(tobiimocap_dict[second][frame-1])
            zmq_socket.send(msgpack.packb((tobiimocap_dict[second][frame-1], mq.get_shifted_time())))

            #key = settings['messaging']['mocaptobii_processing']
            #_mq.publish(exchange='processor', routing_key=key, body=tobiimocap_dict[second][frame-1])

    t1 = Thread(target = runA)
    t1.setDaemon(True)
    t1.start()
    #s1.close()

# Procees tobii input data
def tobiicallback(_mq2, get_shifted_time2, routing_key2, body2):
    context2 = zmq.Context()
    s2 = context2.socket(zmq.SUB)
    s2.setsockopt_string(zmq.SUBSCRIBE, u'')
    s2.connect(body2.get('address'))

    def runB():
        while True:
            data2 = s2.recv()
            tobiibody, localtime2 = msgpack.unpackb(data2, use_list=False)

            # Get tobii localtime
            tobiitime = tobiibody['localtime']

            # First get which second
            second = int(tobiitime)

            # Get decimals to decide which frame
            frame = int(math.modf(tobiitime)[0] * 50)

            # Put in dictionary
            tobiimocap_dict[second][frame]['tobii_' + tobiibody['name']] = tobiibody

    t2 = Thread(target = runB)
    t2.setDaemon(True)
    t2.start()
    #s2.close()

mq = MessageQueue('mocaptobii-processor')
mq.bind_queue(exchange='pre-processor', routing_key=settings['messaging']['mocap_processing'], callback=mocapcallback)
mq.bind_queue(exchange='pre-processor', routing_key=settings['messaging']['tobii_processing'], callback=tobiicallback)

mq.listen()

zmq_socket.send(b'CLOSE')
zmq_socket.close()
