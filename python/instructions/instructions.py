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

IP = "130.237.67.232"

master = Tk()
master.minsize(300,100)
master.geometry("320x100")

# Create pipes to communicate to the client process
pipe_in_client, pipe_out = os.pipe()
pipe_in, pipe_out_client = os.pipe()

# Create a "name" for the client, so that other clients can access by that name
my_client_type = "the_architecture"

# Create a client object to communicate with the server
client = Client(client_type=my_client_type,
                pipe_in=pipe_in_client,
                pipe_out=pipe_out_client,
                host=IP)

# Start the client-process
client.start()

feature_dict = defaultdict(lambda : defaultdict(dict))

def callback():
    print("Next")
    # Sending messages to the server
    #feature_dict[0][0]['TS'] = ''

    feature_dict[0][0]['TS'] = '101010'
    feature_dict[0][0]['S'] = 'S'

    # Sending messages to the server
    my_message = json.dumps(feature_dict[0][0])



    #my_message = json.dumps('S')
    my_message = "interpreter;data;" + my_message + "$"
    # Encode the string to utf-8 and write it to the pipe defined above
    os.write(pipe_out, my_message.encode("utf-8"))
    sys.stdout.flush()

b = Button(master, text="Next", command=callback)
b.pack()

mainloop()

# Close the client safely, not always necessary
client.close() # Tell it to close
client.join() # Wait for it to close
