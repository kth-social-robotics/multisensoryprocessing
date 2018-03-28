# python instructions.py

from Tkinter import *
import subprocess
from collections import defaultdict
import json
from subprocess import PIPE
import sys
sys.path.append('../..')
import os
from os import system
import unicodedata
import numpy
from client import Client
import math
from datetime import datetime
from furhat import connect_to_iristk
from time import sleep

# Server IP
IP = "130.237.67.196"

FURHAT_IP = '130.237.67.115' # Furhat IP address
FURHAT_AGENT_NAME = 'system' # Furhat agent name. Can be found under "Connections" in the furhat web-GUI

# Define window
master = Tk()
master.minsize(500, 300)
master.geometry("520x300")

# Create pipes to communicate to the client process
pipe_in_client, pipe_out = os.pipe()
pipe_in, pipe_out_client = os.pipe()

# Create a "name" for the client, so that other clients can access by that name
my_client_type = "the_instructions"

# Create a client object to communicate with the server
client = Client(client_type=my_client_type,
                pipe_in=pipe_in_client,
                pipe_out=pipe_out_client,
                host=IP)

# Start the client-process
client.start()

# Define dictionary for message
feature_dict = defaultdict(lambda : defaultdict(dict))

# Connect to Furhat
with connect_to_iristk(FURHAT_IP) as furhat_client:
    # Introduce Furhat
    furhat_client.say(FURHAT_AGENT_NAME, 'Hello there. I am here to learn how you are putting this furniture together.')
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

    # Callback when the start button is pressed
    def startCallback():
        # Define time stamp
        time = datetime.now()
        time_stamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:4}".format(\
                      time.year, time.month, time.day, time.hour, time.minute, time.second,\
                      str(time.microsecond)[:3])

        feature_dict[0][0]['TS'] = time_stamp
        feature_dict[0][0]['S'] = 'start'

        # Furhat
        furhat_client.say(FURHAT_AGENT_NAME, 'Okay lets start.')
        furhat_client.gaze(FURHAT_AGENT_NAME, {'x':-2.00,'y':0.00,'z':2.00}) # At default P2 position

        # Print current frame
        print(feature_dict[0][0])

        # Sending messages to the server
        my_message = json.dumps(feature_dict[0][0])

        my_message = "interpreter;data;" + my_message + "$"
        # Encode the string to utf-8 and write it to the pipe defined above
        os.write(pipe_out, my_message.encode("utf-8"))
        sys.stdout.flush()

    # Callback when the next button is pressed
    def nextCallback():
        # Define time stamp
        time = datetime.now()
        time_stamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:4}".format(\
                      time.year, time.month, time.day, time.hour, time.minute, time.second,\
                      str(time.microsecond)[:3])

        feature_dict[0][0]['TS'] = time_stamp
        feature_dict[0][0]['S'] = 'next'

        # Furhat
        furhat_client.say(FURHAT_AGENT_NAME, 'Lets get to the next one.')
        furhat_client.gaze(FURHAT_AGENT_NAME, {'x':3.00,'y':0.00,'z':2.00}) # At default P1 position

        # Print current frame
        print(feature_dict[0][0])

        # Sending messages to the server
        my_message = json.dumps(feature_dict[0][0])

        my_message = "interpreter;data;" + my_message + "$"
        # Encode the string to utf-8 and write it to the pipe defined above
        os.write(pipe_out, my_message.encode("utf-8"))
        sys.stdout.flush()

    # Callback when the end button is pressed
    def endCallback():
        # Define time stamp
        time = datetime.now()
        time_stamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:4}".format(\
                      time.year, time.month, time.day, time.hour, time.minute, time.second,\
                      str(time.microsecond)[:3])

        feature_dict[0][0]['TS'] = time_stamp
        feature_dict[0][0]['S'] = 'end'

        # Furhat
        furhat_client.say(FURHAT_AGENT_NAME, 'It seems like you finished this task. Well done.')
        furhat_client.gaze(FURHAT_AGENT_NAME, {'x':-2.00,'y':0.00,'z':2.00}) # At default P2 position

        # Print current frame
        print(feature_dict[0][0])

        # Sending messages to the server
        my_message = json.dumps(feature_dict[0][0])

        my_message = "interpreter;data;" + my_message + "$"
        # Encode the string to utf-8 and write it to the pipe defined above
        os.write(pipe_out, my_message.encode("utf-8"))
        sys.stdout.flush()

    b1 = Button(master, text="Start", command=startCallback)
    b2 = Button(master, text="Next", command=nextCallback)
    b3 = Button(master, text="End", command=endCallback)
    b1.pack()
    b2.pack()
    b3.pack()

    mainloop()

    # Close the client safely, not always necessary
    client.close() # Tell it to close
    client.join() # Wait for it to close
