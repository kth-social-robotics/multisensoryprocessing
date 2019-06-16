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
import pandas as pd
import numpy as np
from furhat import connect_to_iristk
from time import sleep
import csv
import time, os, fnmatch, shutil
from websocket import create_connection

# Print messages
DEBUG = True

# Furhat connection
ws = create_connection("ws://130.237.67.157:80/api")

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

# Create dataframe
df = pd.DataFrame(columns=['TS', 'Second', 'Frame', 'Speech'])

# Dictionaries (Each key is the local timestamp in seconds. The second key is the frame)
furhat_dict = defaultdict(lambda : defaultdict(dict))
furhat_dict[0][0]['TS'] = ''
furhat_dict[0][0]['S'] = ''
furhat_dict[0][0]['Agent'] = ''
furhat_dict[0][0]['Condition'] = ''
furhat_dict[0][0]['WizardAction'] = ''

# Save to log file
logt = time.localtime()
logtimestamp = time.strftime('%b-%d-%Y_%H%M', logt)
with open('../../logs/experiment2/instructions/instruction_' + logtimestamp + ".csv", 'w') as f:  # Just use 'w' mode in 3.x
    w = csv.DictWriter(f, furhat_dict[0][0].keys(), delimiter=";")
    w.writeheader()

    # Procees feature input data
    def featurecallback(_mq1, get_shifted_time1, routing_key1, body1):
        context1 = zmq.Context()
        s1 = context1.socket(zmq.SUB)
        s1.setsockopt_string(zmq.SUBSCRIBE, u'')
        s1.connect(body1.get('address'))

        def runA():
            while True:
                # Get dataframe
                global df

                data1 = s1.recv()
                featurebody, localtime1 = msgpack.unpackb(data1, use_list=False, encoding='utf-8')

                # Get feature localtime
                featuretime = localtime1

                # First get which second
                second = int(featuretime)

                # Get decimals to decide which frame
                frame = int(math.modf(featuretime)[0] * 50)

                # Put in df
                df_temp = pd.DataFrame([[featuretime, second, frame, str(featurebody['speech'])]], columns=['TS', 'Second', 'Frame', 'Speech'])
                df = df.append(df_temp, ignore_index=True)

                # Print ASR
                if DEBUG: print(featurebody['speech'])

        t1 = Thread(target = runA)
        t1.setDaemon(True)
        t1.start()

    # Process wizard input data
    def wizardcallback(_mq2, get_shifted_time2, routing_key2, body2):
        context2 = zmq.Context()
        s2 = context2.socket(zmq.SUB)
        s2.setsockopt_string(zmq.SUBSCRIBE, u'')
        s2.connect(body2.get('address'))

        def runB():
            while True:
                # Get dataframe
                global df

                data2 = s2.recv()
                wizardbody, localtime2 = msgpack.unpackb(data2, use_list=False, encoding='utf-8')

                # Get wizard localtime
                wizardtime = localtime2

                # First get which second
                second = int(wizardtime)

                # Get decimals to decide which frame
                frame = int(math.modf(wizardtime)[0] * 50)


                print(df)
                # Robot Actions:
                # 1. Start Interaction
                # 2. Next Step
                # 3. End Interaction
                # --------------------
                # User Actions:
                # 4. Correct Action
                # 5. Wrong Action
                # 6. Speech-Where
                # 7. Speech-Which
                # 8. Speech-Repeat
                # 9. Gaze-Object
                # 10. Gaze-Other
                # 11. Gaze-Robot
                # --------------------
                #if key or if action (for now update both and log)
                #csv with instructions and expansions
                # ws.send(
                #     #json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "I already told you I <emphasis level='strong'>really</emphasis> like that person."})
                #     json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "<amazon:breath duration='medium' volume='x-loud'/>Sometimes you want to insert only a single breath."})
                #     #"<amazon:auto-breaths>Amazon Polly is a service that turns text into lifelike speech, allowing you to create applications that talk and build entirely new categories of speech-enabled products. Yeah.</amazon:auto-breaths>"
                # )
                #also print and log what furhat says


                # Put in dictionary
                furhat_dict[second][frame]['TS'] = localtime2
                furhat_dict[second][frame]['Agent'] = str(wizardbody['agent'])
                furhat_dict[second][frame]['Condition'] = str(wizardbody['condition'])
                furhat_dict[second][frame]['WizardAction'] = str(wizardbody['action'])

                # Log to csv file
                w.writerow(furhat_dict[second][frame])
                if DEBUG: print(furhat_dict[second][frame])

                # Remove dict frames when an action is already used and reset pandas df
                #TODO

        t2 = Thread(target = runB)
        t2.setDaemon(True)
        t2.start()

    mq = MessageQueue('furhat-processor')
    #mq.bind_queue(exchange='processor', routing_key=settings['messaging']['feature_processing'], callback=featurecallback)
    mq.bind_queue(exchange='processor', routing_key=settings['messaging']['nlp_data'], callback=featurecallback)
    mq.bind_queue(exchange='processor', routing_key=settings['messaging']['wizard_data'], callback=wizardcallback)

    mq.listen()

    zmq_socket.send(b'CLOSE')
    zmq_socket.close()



    # SPEECH
    # ws.send(
    #     json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "Hello! How are you today? Would you like to build some furniture with me?"})
    # )
    # time.sleep(1)
    # ws.send(
    #     json.dumps({"event_name": "furhatos.event.actions.ActionSpeechStop"})
    # )

    # PROSODY
    #Uh, the one with the <emphasis level="moderate">white</emphasis> stripes! Yeah!
    #reduced, moderate, strong, none
    #https://docs.aws.amazon.com/polly/latest/dg/supported-ssml.html

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

    # ATTEND
    # ws.send(
    #     json.dumps({"event_name": "furhatos.event.actions.ActionAttend", "target": "all")
    # )



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
