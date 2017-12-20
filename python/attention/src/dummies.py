import json
import os
import random
import select
import sys
import threading
import time
from multiprocessing import Process
from .client import Client


class ArchitectureDummy(Process):
    def __init__(self):
        """ Constructor
        """
        super(ArchitectureDummy ,self).__init__()

        # Create a pipe to communicate to the client process
        self.pipe_in_client, self.pipe_out = os.pipe()
        self.pipe_in, self.pipe_out_client = os.pipe()
        # Create a client object to communicate with the server
        self.client = Client(client_type="the_architecture",
                             pipe_in=self.pipe_in_client,
                             pipe_out=self.pipe_out_client)
        self.client.start()

        # Initialize the things that can be sent
        self.y_range = (-30, 30)
        self.x_range = (10, 50)

        self.p1a = ["red", "blue", "left", "right"]
        self.p1n = ["block", "computer", "snus", "lego block"]
        self.p1v = ["pick", "push", "hide"]
        self.p1f = ["","","","","","","","yes"]
        self.p1asr = ["This is an utterance", "This is nonsense", "Danskjavlar"]
        self.pg = ["", "T1", "T2", "T3", "T4", "T5"]
        self.start_time = time.time()

        # Seconds between messages
        self.verb_freq = 5
        self.gaze_freq = 0.5
        self.step_freq = 5
        self.step_th = 0.5

    def run(self):
        verb = Process(target=self._verb_loop)
        verb.start()
        gaze = Process(target=self._gaze_loop)
        gaze.start()
        step = Process(target=self._step_loop)
        step.start()

    def _verb_loop(self):
        while True:
            message = {"TS":str(int(time.time() - self.start_time)),
                       "P1N":[random.choice(self.p1n)],
                       "P1A":[random.choice(self.p1a)],
                       "P1V":[random.choice(self.p1v)],
                       "P1F":[random.choice(self.p1f)],
                       "P1ASR":[random.choice(self.p1asr)]}
            message = "interpreter;data;{}$".format(json.dumps(message))
            os.write(self.pipe_out, message.encode("utf-8"))
            sys.stdout.flush()
            time.sleep(self.verb_freq)
    
    def _gaze_loop(self):
        while True:
            message = {"TS":str(int(time.time() - self.start_time)),
                       "P1G":[random.choice(self.pg)],
                       "P2G":[random.choice(self.pg)],
                       "P1H":[random.choice(self.pg)]}
            message = "interpreter;data;{}$".format(json.dumps(message))
            os.write(self.pipe_out, message.encode("utf-8"))
            sys.stdout.flush()
            time.sleep(self.gaze_freq)

    def _step_loop(self):
        while True:
            if random.random() > self.step_th:
                message = {"TS":str(int(time.time() - self.start_time)),
                           "S":[]}
                message = "interpreter;data;{}$".format(json.dumps(message))
                os.write(self.pipe_out, message.encode("utf-8"))
                sys.stdout.flush()
                time.sleep(self.step_freq)
