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
        self.p1g = [""]
        self.p1h = [""]

        # Seconds between messages
        self.p1a_freq = 5
        self.p1gp_freq = 0.2

    def run(self):
        p1a = Process(target=self._p1a_loop)
        p1a.start()
        p1gp = Process(target=self._p1gp_loop)
        p1gp.start()

    def _p1a_loop(self):
        #print("_p1a_loop")
        while True:
            message = {"P1A":[random.choice(self.p1a)],
                       "P1N":[random.choice(self.p1n)],
                       "P1V":[random.choice(self.p1v)],
                       "P1F":[random.choice(self.p1f)],
                       "P1G":[random.choice(self.p1g)],
                       "P1H":[random.choice(self.p1h)]}
            message = "interpreter;data;{}$".format(json.dumps(message))
            os.write(self.pipe_out, message.encode("utf-8"))
            sys.stdout.flush()
            time.sleep(self.p1a_freq)
    
    def _p1gp_loop(self):
        #print("_p1gp_loop")
        while True:
            message = {"P1GP":[random.randint(self.x_range[0],self.x_range[1])/100,
                               random.randint(self.y_range[0],self.y_range[1])/100]}
            message = "interpreter;data;{}$".format(json.dumps(message))
            os.write(self.pipe_out, message.encode("utf-8"))
            sys.stdout.flush()
            time.sleep(self.p1gp_freq)

class YuMiDummy(Process):
    def __init__(self):
        """ Constructor
        """
        super(YuMiDummy ,self).__init__()

        # Create a pipe to communicate to the client process
        self.pipe_in_client, self.pipe_out = os.pipe()
        self.pipe_in, self.pipe_out_client = os.pipe()
        # Create a client object to communicate with the server
        self.client = Client(client_type="yumi",
                             pipe_in=self.pipe_in_client,
                             pipe_out=self.pipe_out_client)
        self.client.start()

        # Initialize the things that can be sent
        self.y_range = (-30, 30)
        self.x_range = (10, 50)
        self.c_range = (0, 360)
        self.nr_blocks = 10
        self.blocks = []

        # Seconds between messages
        self.upd_freq = 5

    def run(self):
        listener = Process(target=self._tcp_listener, args=(self,))
        listener.start()
        self._update_loop()

    def _tcp_listener(self, parent):
        while True:
            # Wait for incomming message from the server (via the client)
            socket_list = [self.pipe_in]
            # Get the list sockets which are readable
            read_sockets, _, _ = select.select(socket_list, [], [])
            for sock in read_sockets:
                # Incoming message from server
                if sock == self.pipe_in:
                    data = os.read(self.pipe_in, 4096)
                    if not data:
                        #self.log("Disconnected from server")
                        sys.exit()
                    else:
                        parent._remove_block(data.decode("utf-8"))

    def _update_loop(self):
        self.blocks = []
        for bid in range(self.nr_blocks):
            self.blocks.append({"id":bid,
                                "x":random.randint(self.x_range[0], self.x_range[1])/100,
                                "y":random.randint(self.y_range[0], self.y_range[1])/100,
                                "c":random.randint(self.c_range[0], self.c_range[1])})
        while True:
            for block in self.blocks:
                message = "interpreter;update;{}$".format(json.dumps(block))
                os.write(self.pipe_out, message.encode("utf-8"))
                sys.stdout.flush()
                time.sleep(0.1)
            time.sleep(self.upd_freq)

    def _remove_block(self, message):
        message = message.replace("$", "")
        message = message.split(";")
        x_cord = float(message[1].split(",")[0])
        y_cord = float(message[1].split(",")[1])
        print(len(self.blocks))
        for i, block in enumerate(self.blocks):
            print("{} == {} and {} == {}: {}".format(block["x"],
                                                     x_cord,
                                                     block["y"], 
                                                     y_cord, block["x"] == x_cord and block["y"] == y_cord))
            if block["x"] == x_cord and block["y"] == y_cord:
                print("Removing block {} at ({0:.4f}, {0:.4f})".\
                      format(block["id"], block["x"], block["y"]))
                self.blocks.pop(i)
                break
