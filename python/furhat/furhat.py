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

# Define default vars
step = 0
agent = 'none'
condition = 'none'

# Create dataframe
df = pd.DataFrame(columns=['TS', 'Second', 'Frame', 'Speech'])

# Dictionaries (Each key is the local timestamp in seconds. The second key is the frame)
furhat_dict = defaultdict(lambda : defaultdict(dict))
furhat_dict[0][0]['TS'] = ''
furhat_dict[0][0]['S'] = step
furhat_dict[0][0]['Agent'] = agent
furhat_dict[0][0]['Condition'] = condition
furhat_dict[0][0]['WizardAction'] = ''
furhat_dict[0][0]['Action'] = ''
furhat_dict[0][0]['UserSpeech'] = ''

# Save to log file
logt = time.localtime()
logtimestamp = time.strftime('%b-%d-%Y_%H%M', logt)
with open('../../logs/experiment2/instructions/instruction_' + logtimestamp + ".csv", 'w') as f:  # Just use 'w' mode in 3.x
    w = csv.DictWriter(f, furhat_dict[0][0].keys(), delimiter=";")
    w.writeheader()

    # Robot actions
    def robotActions(action):
        #PROSODY: reduced, moderate, strong, none
        global step

        # Start interaction
        if step == 0:
            if "start" in action:
                # Gaze
                #TODO

                # Speech
                ws.send(
                    json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "<amazon:breath duration='medium' volume='x-loud'/>Hi there!"})
                )
                time.sleep(3)
                ws.send(
                    json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "<amazon:breath duration='medium' volume='x-loud'/>Welcome to our experiment. I am <emphasis level='moderate'>really</emphasis> excited to build some furniture with you."})
                )

                # Head nod
                ws.send(
                    json.dumps({"event_name": "furhatos.event.actions.ActionGesture", "name": "Nod"})
                )

                # Ask question
                time.sleep(2.5)
                ws.send(
                    json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "<amazon:breath duration='medium' volume='x-loud'/>Are you ready to start?"})
                )

                # Update step
                step = 0.1
                return

        # Demographics
        elif step == 0.1:
            if "yes" in action:
                if "action" in condition:
                    # Gaze
                    #TODO

                    # Speech
                    ws.send(
                        json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "<amazon:breath duration='medium' volume='x-loud'/>Brilliant! Have you built IKEA furniture before?"})
                    )

                    # Update step
                    step = 0.2
                    return

        elif step == 0.2:
            if "yes" in action:
                if "action" in condition:
                    # Gaze
                    #TODO

                    # Speech
                    ws.send(
                        json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "<amazon:breath duration='medium' volume='x-loud'/>I wish I could build one myself, but for now I am going to help you with the instructions."})
                    )
                    time.sleep(2)
                    ws.send(
                        json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "<amazon:breath duration='medium' volume='x-loud'/>Should we start?"})
                    )

                    # Head nod
                    time.sleep(2.5)
                    ws.send(
                        json.dumps({"event_name": "furhatos.event.actions.ActionGesture", "name": "Nod"})
                    )

                    # Update step
                    step = 1
                    return

        elif step == 1:
            if "yes" in action:
                if "action" in condition:
                    # Gaze
                    #TODO

                    # Speech
                    ws.send(
                        json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "<amazon:breath duration='medium' volume='x-loud'/>Great!"})
                    )
                    # Instruction - Expansions 1, 2 and 3
                    time.sleep(1)
                    ws.send(
                        json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "<amazon:breath duration='medium' volume='x-loud'/>Let's start with the big piece on the table. It is the one on your right. Uhm, the one with the white stripes, next to the black piece."})
                    )

                    # Update step
                    step = 1.1
                    return
            # else:
            #     # Gaze
            #     #TODO
            #
            #     # Speech
            #     ws.send(
            #         json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "<amazon:breath duration='medium' volume='x-loud'/>I did not get that! Can you please repeat?"})
            #     )
            #
            #     return

        elif step == 1.1:
            if "correct" in action:
                if "action" in condition:
                    # Gaze
                    #TODO

                    # Speech
                    ws.send(
                        json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "<amazon:breath duration='medium' volume='x-loud'/>Great! You can put it on your right for now. Let's get to the next one."})
                    )

                    # Head nod
                    time.sleep(1)
                    ws.send(
                        json.dumps({"event_name": "furhatos.event.actions.ActionGesture", "name": "Nod"})
                    )

                    # Update step
                    step = 2
                    return
            if "wrong" in action:
                if "action" in condition:
                    # Gaze
                    #TODO

                    # Speech
                    ws.send(
                        json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "<amazon:breath duration='medium' volume='x-loud'/>Uhm, this does not seem to be the right one."})
                    )

                    # Head nod
                    time.sleep(1)
                    ws.send(
                        json.dumps({"event_name": "furhatos.event.actions.ActionGesture", "name": "Shake"})
                    )

                    return

        # elif step == 99:
        #     if "action" in condition:
        #         # Gaze
        #         #TODO
        #
        #         # Speech
        #         ws.send(
        #             json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "<amazon:breath duration='medium' volume='x-loud'/>It seems like we have collected all the right pieces. Now it is time to assemble them together!"})
        #         )
        #
        #         # Head nod
        #         time.sleep(1)
        #         ws.send(
        #             json.dumps({"event_name": "furhatos.event.actions.ActionGesture", "name": "Nod"})
        #         )
        #
        #         return

        # else:
        #     # Gaze
        #     #TODO
        #
        #     # Speech
        #     ws.send(
        #         json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "<amazon:breath duration='medium' volume='x-loud'/>Something seems to be wrong."})
        #     )
        #
        #     return

        # Print robot action
        print("Robot:", action)

        # ws.send(
        #     json.dumps({"event_name": "furhatos.event.actions.ActionGaze", "location": {"x": -0.1, "y": -0.2, "z": +1}, "mode": 0, "gazeSpeed": 2})
        # )

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

                # Check gaze
                #TODO

                # Get speech
                speech = str(featurebody['speech'])

                # Put asr in df
                df_temp = pd.DataFrame([[featuretime, second, frame, speech]], columns=['TS', 'Second', 'Frame', 'Speech'])
                df = df.append(df_temp, ignore_index=True)

                # Print ASR
                print(speech)

                # Check speech
                if "yes" in speech:
                    _speech = df.Speech.values.tolist()

                    # Put in dictionary
                    furhat_dict[second][frame]['TS'] = localtime1
                    furhat_dict[second][frame]['S'] = step
                    furhat_dict[second][frame]['Agent'] = agent
                    furhat_dict[second][frame]['Condition'] = condition
                    furhat_dict[second][frame]['Action'] = 'yes'
                    furhat_dict[second][frame]['UserSpeech'] = _speech

                    # Log to csv file
                    w.writerow(furhat_dict[second][frame])
                    if DEBUG: print(furhat_dict[second][frame])

                    # Tell robot what to do
                    robotActions("yes")

                    # Reset df
                    df = pd.DataFrame(columns=['TS', 'Second', 'Frame', 'Speech'])
                else:
                    _speech = df.Speech.values.tolist()

                    # Put in dictionary
                    furhat_dict[second][frame]['TS'] = localtime1
                    furhat_dict[second][frame]['S'] = step
                    furhat_dict[second][frame]['Agent'] = agent
                    furhat_dict[second][frame]['Condition'] = condition
                    furhat_dict[second][frame]['Action'] = 'misunderstood'
                    furhat_dict[second][frame]['UserSpeech'] = _speech

                    # Log to csv file
                    w.writerow(furhat_dict[second][frame])
                    if DEBUG: print(furhat_dict[second][frame])

                    # Tell robot what to do
                    robotActions("misunderstood")

                    # Reset df
                    df = pd.DataFrame(columns=['TS', 'Second', 'Frame', 'Speech'])

                # Check action
                #TODO

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
                global step
                global agent
                global condition

                data2 = s2.recv()
                wizardbody, localtime2 = msgpack.unpackb(data2, use_list=False, encoding='utf-8')

                # Get wizard localtime
                wizardtime = localtime2

                # First get which second
                second = int(wizardtime)

                # Get decimals to decide which frame
                frame = int(math.modf(wizardtime)[0] * 50)

                # Tell robot what to do
                # Robot Actions:
                # 1. Start Interaction
                if wizardbody['action'] == '1':
                    robotActions("start")
                # 2. Next Step
                elif wizardbody['action'] == '2':
                    robotActions("instruct")
                # 3. Expand Step
                elif wizardbody['action'] == '3':
                    robotActions("expand")
                # 4. End Interaction
                elif wizardbody['action'] == '4':
                    robotActions("end")
                # User Actions:
                # 11. Correct Action
                elif wizardbody['action'] == '11':
                    robotActions("correct")
                # 12. Wrong Action
                elif wizardbody['action'] == '12':
                    robotActions("wrong")
                # 13. Speech-Where
                elif wizardbody['action'] == '13':
                    robotActions("where")
                # 14. Speech-Which
                elif wizardbody['action'] == '14':
                    robotActions("which")
                # 15. Speech-Repeat
                elif wizardbody['action'] == '15':
                    robotActions("repeat")
                # 16. Gaze-Object
                elif wizardbody['action'] == '16':
                    robotActions("gaze_object")
                # 17. Gaze-Other
                elif wizardbody['action'] == '17':
                    robotActions("gaze_other")
                # 18. Gaze-Robot
                elif wizardbody['action'] == '18':
                    robotActions("gaze_robot")

                # Put in dictionary
                agent = str(wizardbody['agent'])
                condition = str(wizardbody['condition'])

                furhat_dict[second][frame]['TS'] = localtime2
                furhat_dict[second][frame]['S'] = step
                furhat_dict[second][frame]['Agent'] = agent
                furhat_dict[second][frame]['Condition'] = condition
                furhat_dict[second][frame]['WizardAction'] = str(wizardbody['action'])

                # Log to csv file
                w.writerow(furhat_dict[second][frame])
                if DEBUG: print(furhat_dict[second][frame])

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
