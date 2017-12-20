import ast
import csv
import errno
import json
import os
import re
import select
import sys
import time
from datetime import datetime
from multiprocessing import Process

from .client import Client
from .data_handler import DataHandler

class Interpreter(Process):
    """ The Interpreter-class is a intermediator between the arcitecture and the ROS-network.
    """
    def __init__(self, log_queue=None):
        """ Constructor
        param: data_base_file [path]
        return: Interpreter [Process]
        """
        super(Interpreter, self).__init__()
        self.log_queue = log_queue
        # Create a pipe to communicate to the client process
        self.pipe_in_client, self.pipe_out = os.pipe()
        self.pipe_in, self.pipe_out_client = os.pipe()

        # Create a client object to communicate with the server
        self.client = Client(client_type="interpreter",
                             pipe_in=self.pipe_in_client,
                             pipe_out=self.pipe_out_client)
        self.client.start()

        # Check that the data file is correct.
        if data_file:
            if os.path.isfile(data_file):
                # Read data base and format it.
                self.data_handler = DataHandler(data_file, log_queue=log_queue)
            else:
                self.log("Error, Data file does not exist: {}".format(data_file))
                raise OSError(data_file)
        else:
            pass
            #self.log("Error, No data file given, you are using this module wrong, ask Olov")
            #raise OSError

        # Create and initialize the variables
        self.current_action = None
        self.action_dict = {}
        self.reset()

    def run(self):
        """ Main loop.
        param: N/A
        return: N/A
        """
        while True:
            # Wait for incomming message from the server (via the client)
            socket_list = [self.pipe_in]

            # Get the list sockets which are readable
            read_sockets, _, _ = select.select(socket_list, [], [])

            for sock in read_sockets:
                # Incoming message from remote server
                if sock == self.pipe_in:
                    data = os.read(self.pipe_in, 4096)
                    if not data:
                        self.log("Disconnected from server")
                        sys.exit()
                    else:
                        self.parse(data.decode("utf-8"))

    def parse(self, data):
        """ Interperet the incomming message and take appropriate action.
        param: data [String, format defined in README.md]
        return: N/A
        """
        self.log("Parsing data: {}".format(data))
        try:
            data = data.replace("$", "")
            data = ast.literal_eval(data)
            if data["feedback"]:
                self.confirm(data)
            else:
                self.action(data)
        except ValueError:
            data = data.split(";")
            header = data.pop(0)
            if header == "update":
                self.update(data)
            else:
                self.log("Unknown request: {}".format(header))

    def confirm(self, data):
        """ Interperet the confirm message, either positive or negative, i.e. either tell YuMi to
        execute the action or test a new block.
        param: data [dict]
        return: N/A
        """
        # If a confirmation is recieved, send execute command to yumi, remove the block from the 
        # data base and send a speech command to hololens.
        if "yes" in data["feedback"]:
            self.send("yumi;execute$")
            time.sleep(1)
            self.send("hololens;speech;ok$")
        # If a negation is recieved and there are blocks still in the list then try the next block
        # in the list, else start over.
        else:
            if self.data_handler.current_filter:
                current_block = self.data_handler.get_next_block()
                self.send("yumi;{};{},{}$".format(self.current_action,
                                                  current_block["x"],
                                                  current_block["y"]))
            else:
                self.reset()

    def action(self, data):
        """ Parse the actions from the architecture.
        param: action_msg [dict]
        return: N/A
        {'P1V': [], 'P1A': ['blue'], 'objects': ['lego'], 'feedback': []}
        """

        # If there are skills within the message, update the current skills to the first on in the 
        # list of skills.
        if data["P1V"]:
            self.current_action = data["skills"][0]
        self.data_handler.filter(data["P1A"])
        
        # No objects are found, the current turn is restarted.
        if not self.data_handler.current_filter:
            self.reset()
        # If only a few objects remain in the data base, the action is visualized to the user.
        elif len(self.data_handler.current_filter) < 4:
            current_block = self.data_handler.get_next_block()
            self.send("yumi;{};{},{}$".format(self.current_action,
                                              current_block["x"],
                                              current_block["y"]))
        # If there are many objects left the hololens will highlight the ones considered
        else:
            msg = []
            for item in self.data_handler.get_all_considered():
                msg.append("{},{},{}".format(item["id"], item["x"][:5], item["y"][:5]))
            msg = ";".join(msg)
            msg = "{};{}$".format("hololens", msg)
            self.send(msg)

    def update(self, update_msg):
        """ Update the data-base
            param: update_msg [String, format defined in README.md]
            return: N/A
        """
        update_msg = update_msg.replace("$", "")
        update_msg = update_msg.split(";")
        for block in update_msg:
            block = block.split(",")
            if len(block) > 1:
                update_dict = {"x":block[0], "y":block[1]}
                if len(block) > 2:
                    update_dict[block[2].split(":")[0]] = block[2].split(":")[1]
                if len(block) > 3:
                    update_dict[block[3].split(":")[0]] = block[3].split(":")[1]
                self.data_handler.update(update_dict)

    def _send(self, msg):
        """ Sends a message
            param: msg [String]
            return: None
        """
        self.log("Interpreter is sending: {}".format(msg))
        os.write(self.pipe_out, msg.encode("utf-8"))
        sys.stdout.flush()

    def reset(self):
        """ Reset the variables for a new round.
            param: N/A
            return: None
        """
        self.current_action = None
        self.action_dict = {}
        self.current_block = None
        self.data_handler.reset_filter()

    def log(self, message):
        """ Send the message to the log queue
            params: message [String]
            return: None
        """
        if self.log_queue:
            self.log_queue.put("Interpreter#{}".format(message))
    
    def print_state(self):
        print("======Interpeter state======")
        print("current action:\t{}".format(self.current_action))
        print("nr items      :\t{}".format(len(self.data_handler.current_filter)))
        print("current attributes:")
        for attribute in self.data_handler.current_attributes:
            print("\t{}".format(attribute))
