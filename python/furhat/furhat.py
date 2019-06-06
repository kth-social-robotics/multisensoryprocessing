# python3 furhat.py

import zmq
import pika
import json
import time
import msgpack
import re
import sys
sys.path.append('..')
from shared import MessageQueue
import yaml
from collections import defaultdict
import math
from shared import create_zmq_server, MessageQueue
from threading import Thread
import subprocess
from subprocess import PIPE
import os
from os import system
import unicodedata
import numpy
from furhat import connect_to_iristk
from time import sleep
import csv
import time, os, fnmatch, shutil
from websocket import create_connection

# Print messages
DEBUG = True

# Settings
SETTINGS_FILE = '../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Define server
zmq_socket, zmq_server_addr = create_zmq_server()
mq = MessageQueue('furhat-processor')

mq.publish(
    exchange='processor',
    routing_key=settings['messaging']['furhat_processing'],
    body={'address': zmq_server_addr, 'file_type': 'txt'}
)

# Dictionaries
furhat_dict = defaultdict(lambda : defaultdict(dict))

# Each key is the local timestamp in seconds. The second key is the frame
# Time, Frame: Timestamp,
# P1 Test
# Step

furhat_dict[0][0]['TS'] = ''
furhat_dict[0][0]['P1TEST'] = ['']
furhat_dict[0][0]['S'] = ''

# Procees feature input data
def featurecallback(_mq1, get_shifted_time1, routing_key1, body1):
    context1 = zmq.Context()
    s1 = context1.socket(zmq.SUB)
    s1.setsockopt_string(zmq.SUBSCRIBE, u'')
    s1.connect(body1.get('address'))

    def runA():
        while True:
            data1 = s1.recv()
            featurebody, localtime1 = msgpack.unpackb(data1, use_list=False, encoding='utf-8')

            # Get feature localtime
            featuretime = localtime1

            # First get which second
            second = int(featuretime)

            # Get decimals to decide which frame
            frame = int(math.modf(featuretime)[0] * 50)

            print(featurebody)

    t1 = Thread(target = runA)
    t1.setDaemon(True)
    t1.start()

mq = MessageQueue('furhat-processor')
mq.bind_queue(exchange='processor', routing_key=settings['messaging']['feature_processing'], callback=featurecallback)

mq.listen()

zmq_socket.send(b'CLOSE')
zmq_socket.close()



ws = create_connection("ws://192.168.1.133:80/api")

# SPEECH
# ws.send(
#     json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "Hello! How are you today? Would you like to build some furniture with me?"})
# )
# time.sleep(1)
# ws.send(
#     json.dumps({"event_name": "furhatos.event.actions.ActionSpeechStop"})
# )

# GESTURES
# ws.send(
#     json.dumps({"event_name": "furhatos.event.actions.ActionGesture", "name": "Nod"})
# )
# ws.send(
#     json.dumps({"event_name": "furhatos.event.actions.ActionGesture", "name": "Shake"})
# )

# GAZE
# ws.send(
#     json.dumps({"event_name": "furhatos.event.actions.ActionGaze", "location": {"x": -0.1, "y": -0.2, "z": +1}, "mode": 0, "gazeSpeed": 2})
# )



# Uncomment for furhat and indent
    # # Connect to Furhat
    # with connect_to_iristk(FURHAT_IP) as furhat_client:
    #     # Introduce Furhat
    #     furhat_client.say(FURHAT_AGENT_NAME, 'It seems like I can now hear what you are saying.')
    #     #furhat_client.gaze(FURHAT_AGENT_NAME, {'x':3.00,'y':0.00,'z':2.00}) # At default P1 position
    #     furhat_client.gaze(FURHAT_AGENT_NAME, {'x':-2.00,'y':0.00,'z':2.00}) # At default P2 position
    #
    #     # Log Furhat events
    #     def event_callback(event):
    #         #print(event) # Receives each event the furhat sends out.
    #         fd = open('../../../logs/furhat_log.csv','a')
    #         fd.write(event)
    #         fd.write('\n')
    #         fd.close()
    #
    #     # Listen to events
    #     furhat_client.start_listening(event_callback) # register the event callback receiver
# Uncomment for furhat and indent



# from furhat import connect_to_iristk
# from time import sleep
#
# FURHAT_IP = '130.237.67.115' # Furhat IP address
# FURHAT_AGENT_NAME = 'system' # Furhat agent name. Can be found under "Connections" in the furhat web-GUI
#
# def convert_to_furhat_coordinates(furhat_position, object_position):
#     return [ object_position[2] - furhat_position[2], object_position[1] - furhat_position[1], - (object_position[0] - furhat_position[0])]
#
# with connect_to_iristk(FURHAT_IP) as furhat_client:
#     #def event_callback(event):
#         #print(event) # Receives each event the furhat sends out.
#
#     # Listen to events
#     #furhat_client.start_listening(event_callback) # register our event callback receiver
#
#     # Speak
#     furhat_client.say(FURHAT_AGENT_NAME, 'hello humans')
#
#     # Head Limits
#     # X from -1 (right) to +1 (left)
#     # Y from -1 (down) to +1 (up)
#     # Z from 0 to 2 (forwards)
#     # Gaze can go further
#
#     # Coordinates from mocap
#     furhat_position = [-1.02193, 0.96456 + 0.2, 2.74624]
#     object_position1 = [-2.74473, 0.7612, 3.37574]
#     object_position2 = [-2.267, 1.152, 3.735]
#
#     # Convert to mocap space
#     object_coordinates_furhat_space = convert_to_furhat_coordinates(furhat_position, object_position1)
#     print(object_coordinates_furhat_space)
#     furhat_client.gaze(FURHAT_AGENT_NAME, {'x': object_coordinates_furhat_space[0], 'y': object_coordinates_furhat_space[1],'z': object_coordinates_furhat_space[2]})
#     sleep(0.01)
#
#     object_coordinates_furhat_space = convert_to_furhat_coordinates(furhat_position, object_position2)
#     print(object_coordinates_furhat_space)
#     furhat_client.gaze(FURHAT_AGENT_NAME, {'x': object_coordinates_furhat_space[0], 'y': object_coordinates_furhat_space[1],'z': object_coordinates_furhat_space[2]})
#     sleep(0.01)
#
#     # Continuous gaze
#     # for i in range(10,-10,-1):
#     #     furhat_client.gaze(FURHAT_AGENT_NAME, {'x':i/10,'y':i/10,'z':2.00})
#     #     sleep(0.1)
#
#     furhat_client.say(FURHAT_AGENT_NAME, 'I gazed')
#     sleep(0.01)



# ws.send(
#     json.dumps({"event_name": "furhatos.event.actions.ActionGaze", "location": {"x": -0.1, "y": -0.2, "z": +1}, "mode": 0, "gazeSpeed": 2})
# )
# ws.send(
#     json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "Next, you should take the white piece to put on top."})
# )
# time.sleep(1.5)
# ws.send(
#     json.dumps({"event_name": "furhatos.event.actions.ActionGaze", "location": {"x": -0.4, "y": -0.4, "z": +1}, "mode": 0, "gazeSpeed": 2})
# )
# time.sleep(3)
# ws.send(
#     json.dumps({"event_name": "furhatos.event.actions.ActionGaze", "location": {"x": -0.1, "y": -0.2, "z": +1}, "mode": 0, "gazeSpeed": 2})
# )
# ws.send(
#     json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "It is the one with the black stripes."})
# )
# time.sleep(1.5)
# ws.send(
#     json.dumps({"event_name": "furhatos.event.actions.ActionGaze", "location": {"x": -0.4, "y": -0.4, "z": +1}, "mode": 0, "gazeSpeed": 2})
# )
# ws.send(
#     json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "On your left."})
# )
ws.send(
    json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "Yeah."})
)
ws.send(
    json.dumps({"event_name": "furhatos.event.actions.ActionGesture", "name": "Nod"})
)
