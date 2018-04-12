# python2 instructions.py
# python instructions.py

import Tkinter as tk
from Tkinter import Frame, Tk, Button
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
from playsound import playsound
from PIL import Image, ImageTk

# Server IP
IP = "130.237.67.237"

FURHAT_IP = '130.237.67.115' # Furhat IP address
FURHAT_AGENT_NAME = 'system' # Furhat agent name. Can be found under "Connections" in the furhat web-GUI

# Define window
master = tk.Tk()
master.minsize(1270, 750)
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

# Uncomment for furhat and indent
# Connect to Furhat
# with connect_to_iristk(FURHAT_IP) as furhat_client:
#     # Introduce Furhat
#     furhat_client.say(FURHAT_AGENT_NAME, 'You will instruct the builder on how to construct this item.')
#     furhat_client.gaze(FURHAT_AGENT_NAME, {'x':3.00,'y':0.00,'z':2.00}) # At default P1 position
#     #furhat_client.gaze(FURHAT_AGENT_NAME, {'x':-2.00,'y':0.00,'z':2.00}) # At default P2 position
#     # Log Furhat events
#     def event_callback(event):
#         #print(event) # Receives each event the furhat sends out.
#         fd = open('../../logs/furhat_log.csv','a')
#         fd.write(event)
#         fd.write('\n')
#         fd.close()
#     # Listen to events
#     furhat_client.start_listening(event_callback) # register the event callback receiver
# Uncomment for furhat and indent

# Define photos for instructions
photo0 = 'photos/0.png'
photo1 = "photos/1.png"
photo2 = "photos/2.png"
photo3 = "photos/3.png"
photo4 = "photos/4.png"
photo5 = "photos/5.png"
photo6 = "photos/6.png"
photo7 = "photos/7.png"
photo8 = "photos/8.png"
photo9 = "photos/9.png"
master.photos = {}
master.photos[0] = ImageTk.PhotoImage(Image.open(photo0))
master.photos[1] = ImageTk.PhotoImage(Image.open(photo1))
master.photos[2] = ImageTk.PhotoImage(Image.open(photo2))
master.photos[3] = ImageTk.PhotoImage(Image.open(photo3))
master.photos[4] = ImageTk.PhotoImage(Image.open(photo4))
master.photos[5] = ImageTk.PhotoImage(Image.open(photo5))
master.photos[6] = ImageTk.PhotoImage(Image.open(photo6))
master.photos[7] = ImageTk.PhotoImage(Image.open(photo7))
master.photos[8] = ImageTk.PhotoImage(Image.open(photo8))
master.photos[9] = ImageTk.PhotoImage(Image.open(photo9))

# Last photo
end = 9

# Callback when the button is pressed
def nextCallback(index, end):
    # Define time stamp
    time = datetime.now()
    time_stamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:4}".format(\
                  time.year, time.month, time.day, time.hour, time.minute, time.second,\
                  str(time.microsecond)[:3])

    # Define feature dict
    feature_dict[0][0]['TS'] = time_stamp
    if index == 0:
        feature_dict[0][0]['S'] = 'start'
    elif index == end - 1:
        feature_dict[0][0]['S'] = 'end'
    else:
        feature_dict[0][0]['S'] = 'next'

# Uncomment for Furhat
    # # Furhat
    # if index == 0:
    #     furhat_client.say(FURHAT_AGENT_NAME, 'Okay lets start.')
    #     furhat_client.gaze(FURHAT_AGENT_NAME, {'x':-2.00,'y':0.00,'z':2.00}) # At default P2 position
    # elif index == end - 1:
    #     furhat_client.say(FURHAT_AGENT_NAME, 'It seems like you finished this task. Well done.')
    #     furhat_client.gaze(FURHAT_AGENT_NAME, {'x':-2.00,'y':0.00,'z':2.00}) # At default P2 position
    # else:
    #     furhat_client.say(FURHAT_AGENT_NAME, 'Lets get to the next one.')
    #     furhat_client.gaze(FURHAT_AGENT_NAME, {'x':3.00,'y':0.00,'z':2.00}) # At default P1 position
# Uncomment for Furhat

    # Print current frame
    print(feature_dict[0][0])

    # Update index
    global global_index
    global_index = index + 1

    # Update screen
    vlabel.configure(image = master.photos[global_index])

    # Sending messages to the server
    my_message = json.dumps(feature_dict[0][0])
    my_message = "interpreter;data;" + my_message + "$"
    # Encode the string to utf-8 and write it to the pipe defined above
    os.write(pipe_out, my_message.encode("utf-8"))
    sys.stdout.flush()

    # Send sync signal
    playsound('beep.mp3')

def wrongCallback(index):
    # Define time stamp
    time = datetime.now()
    time_stamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:4}".format(\
                  time.year, time.month, time.day, time.hour, time.minute, time.second,\
                  str(time.microsecond)[:3])

    # Define feature dict
    feature_dict[0][0]['TS'] = time_stamp
    feature_dict[0][0]['S'] = str(index) + '_wrong'

# Uncomment for Furhat
    # # Furhat
    # furhat_client.say(FURHAT_AGENT_NAME, 'It seems that is not right.')
    # furhat_client.gaze(FURHAT_AGENT_NAME, {'x':3.00,'y':0.00,'z':2.00}) # At default P1 position
# Uncomment for Furhat

    # Print current frame
    print(feature_dict[0][0])

    # Sending messages to the server
    my_message = json.dumps(feature_dict[0][0])
    my_message = "interpreter;data;" + my_message + "$"
    # Encode the string to utf-8 and write it to the pipe defined above
    os.write(pipe_out, my_message.encode("utf-8"))
    sys.stdout.flush()

    # Send wrong signal
    playsound('wrong.mp3')

# Define first photo
vlabel = tk.Label(master, image = master.photos[0])
vlabel.pack()

# Set index
global_index = 0

b1 = tk.Button(master, text="Next", command=lambda: nextCallback(global_index, end))
b2 = tk.Button(master, text="Wrong", command=lambda: wrongCallback(global_index))
#b1.pack()
#b2.pack()

# Get key read from the presenter
def key(event):
    #Up Left: u'\uf72c'
    #Up Right: u'\uf72d'
    #Down Left: u'\uf708'
    #Down Right: '.'

    # Up Left: Wrong item
    if repr(event.char) == "u'\uf72c'":
        wrongCallback(global_index)

    # Up Right: Next step (Right item)
    if repr(event.char) == "u'\uf72d'":
        nextCallback(global_index, end)

# Frame for detecting key events
frame = Frame(master, highlightbackground="green", highlightcolor="green", highlightthickness=1, width=100, height=100, bd=0)
frame.bind("<Key>", key)
frame.focus_force()
frame.pack(side="left", fill="both", expand=True)

tk.mainloop()

# Close the client safely, not always necessary
client.close() # Tell it to close
client.join() # Wait for it to close
