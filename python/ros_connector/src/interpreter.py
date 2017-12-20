""" Module doc string
"""
import ast
import math
import os
import select
import sys
from multiprocessing import Process
import time
import threading
from .client import Client


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

        # Create and initialize the variables
        self.print_every = 1.0
        self.likelihood_threshold = 1.2
        self.current_action = "pick"
        self.known_attr = ["red", "blue", "green", "yellow"]
        self.attention_table = []
        self.first_verbal = False
        self.first_disamb = False
        self._reset()

    def _reset(self):
        self.current_action = "pick"
        self.attention_table = []
        self.first_verbal = False
        self.first_disamb = False

    def run(self):
        """ Main loop. Simply read messages from the server and send them to self._parse() to take
        appropriate action. 
        param: N/A
        return: N/A
        """
        self._print_blocks()
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
                        self._parse(data.decode("utf-8"))

    def _parse(self, data):
        """ Interperet the incomming message and take appropriate action.
        param: data [String, format defined in README.md]
        return: N/A
        """
        #self.log("Parsing data: {}".format(data))
        
        # Preporcess the data message.
        data = data.replace("$", "")
        data = data.split(";")
        for i in range(1, len(data)):
            try:
                data[i] = ast.literal_eval(data[i])
            except SyntaxError:
                return
        if data[0] == "update":
            self._update_block_array(data)
        elif data[0] == "data":
            self._disambiguate(data)
        else:
            self.log("Unknown message type: {}".format(data[0]))

    def _disambiguate(self, data):
        data = data[1]
        p1a = []
        attention_pos = []
        # Extract verbal requests
        if "P1A" in data.keys():
            p1a = [attr for attr in data["P1A"] if attr in self.known_attr]
        # Extract gaze
        if "P1GP" in data.keys():
            attention_pos = data["P1GP"]
        min_dist = None
        attention_block = None
        if attention_pos:
            min_dist = 10000
        # Set the first_disamb flag to indicate that there exists information.
        if p1a and self.attention_table:
            self.first_disamb = True

        # Iterate through the blocks and filter
        for block in self.attention_table:
            # Handle verbal attribute
            if p1a and not block["c"] in p1a:
                block["include"] = False
            elif p1a and block["c"] in p1a:
                block["include"] = True
            # Handle gaze
            if attention_pos:
                dist = self._dist([block["x"], block["y"]], attention_pos)
                if dist < min_dist:
                    min_dist = dist
                    attention_block = block
        if attention_block:
            attention_block["at"] += 1

        # Iterate through the blocks and calculate likelihood
        inc_list = [block["at"] for block in self.attention_table if block["include"]]
        nr_block = len(inc_list)
        tot_att = sum(inc_list)
        tot_lh = 0
        for block in self.attention_table:
            if block["include"]:
                if not tot_att == 0:
                    lh = (1/float(nr_block)) * (block["at"]/float(tot_att))
                else:
                    lh = (1/float(nr_block))
                tot_lh += lh
                block["lh"] = lh
            else:
                block["lh"] = 0.0
        if not tot_lh:
            tot_lh = len(self.attention_table)
        for block in self.attention_table:
            block["lh"] = block["lh"]/tot_lh
        
        # Test if the likelihood is high enough, if so execute command. If the likelihood is not 
        # high enough but there is a positive feedback in the P1F message then the action should 
        # be executed any way.
        if "P1F" in data.keys():
            if "yes" in data["P1F"]:
                self._test_if_execute(th=0)
            elif "no" in data["P1F"]:
                self._forget_info()
                return
            else:
                self._test_if_execute()
        else:
            self._test_if_execute()
        #self._test_if_execute()

    def _forget_info(self):
        """ Forget the information and start over.
        """
        if self.attention_table:
            for block in self.attention_table:
                block["lh"] = 0
                block["at"] = 0
                block["include"] = True
        self.first_disamb = False

    def _test_if_execute(self, th=None):
        """ Test if the likelihood is high enough, if so send a execute command to YuMi.
        """
        if th is None:
            th = self.likelihood_threshold

        if not self.first_disamb:
            return True
        # Extract the block with the highest likelihood
        most_likely_block = sorted(self.attention_table, key=lambda k: k['lh'], reverse=True)[0]
        if most_likely_block["lh"] >= th:
            self._send("yumi;{};{};{}$".format(self.current_action,
                                              most_likely_block["x"],
                                              most_likely_block["y"]))
            self._reset()
            return True
        return False

    def _dist(self, pos1, pos2):
        """ Calculate and return the euclidean distance.
        """
        return math.sqrt(sum([(a - b) ** 2 for a, b in zip(pos1, pos2)]))
    
    def _update_block_array(self, data):
        """ Update the self.attention_table list either add new blocks or edit their positions and colors. 
        """
        data.pop(0)
        for new_block in data:
            # Test if the object has been seen before using its id.
            block_in_list = next((item for item in self.attention_table if item["id"] == new_block["id"]), None)
            if block_in_list:
                # This block is already in the list, update the list
                for key, value in new_block.items():
                     block_in_list[key] = value
            else:
                # This block was not in the list, add it
                new_block["lh"] = 0
                new_block["at"] = 0
                new_block["include"] = True
                self.attention_table.append(new_block)
        # Iterate through the blocks and comform the HSV colors to string values.
        for block in self.attention_table:
            if isinstance(block["c"], int):
                block["c"] = self._hsv_to_string(block["c"])
        #self._print_blocks()
    
    def _print_blocks(self):
        threading.Timer(self.print_every, self._print_blocks).start()
        clear = "\n" * 100
        #while True:
        print(clear)
        print("_"*124)
        print_list = []
        if self.attention_table:
            print_list = sorted(self.attention_table, key=lambda k: k['id'])
            highest_lh = sorted(self.attention_table, key=lambda k: k['lh'], reverse=True)[0]
            header = ["id", "x", "y", "c", "at", "include", "lh"]  
            header_str = ""
            for col in header:
                header_str += "{:<11}".format(col)
            print(header_str)
        row_str = ""
        for block in print_list:
            for col in header:
                if col == "lh":
                    nr_lines = int(block[col]*50)
                    nr_white = 50 - nr_lines
                    str_ = "[" + "|"*nr_lines + " "*nr_white + "] {0:.2f}%".format(block[col]*100)
                elif isinstance(block[col], float):
                    str_ = "{0:.4f}".format(block[col])
                else:
                    str_ = str(block[col])
                row_str += "{:<11}".format(str_)
            if highest_lh["id"] == block["id"]:
                row_str += "\t<=="
            row_str += "\n"
        print(row_str)
        print("_"*124)

    def _hsv_to_string(self, hsv):
        hsv *= 2
        # Test if yellow
        if hsv > 30 and hsv <= 90:
            return "yellow"
        # Test if green
        elif hsv > 90 and hsv <= 180:
            return "green"
        elif hsv > 180 and hsv <= 300:
            return "blue"
        return "red"

    def _send(self, msg):
        """ Sends a message
            param: msg [String]
            return: None
        """
        #self.log("Interpreter is sending: {}".format(msg))
        os.write(self.pipe_out, msg.encode("utf-8"))
        sys.stdout.flush()

    def log(self, message):
        """ Send the message to the log queue
            params: message [String]
            return: None
        """
        if self.log_queue:
            self.log_queue.put("Interpreter#{}".format(message))
