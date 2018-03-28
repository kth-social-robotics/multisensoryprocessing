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

# Server IP
IP = "130.237.67.196"

# Define window
master = Tk()
master.minsize(500,300)
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

# Callback when the button is pressed
def callback():
    print("Next step.")
    # Define time stamp
    time = datetime.now()
    time_stamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:4}\t".format(\
                  time.year, time.month, time.day, time.hour, time.minute, time.second,\
                  str(time.microsecond)[:3])

    feature_dict[0][0]['TS'] = time_stamp
    feature_dict[0][0]['S'] = 'Sn'

    # Sending messages to the server
    my_message = json.dumps(feature_dict[0][0])

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
