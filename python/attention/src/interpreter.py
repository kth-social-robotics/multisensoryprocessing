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
import csv
import collections
from furhat import connect_to_iristk
from time import sleep

FURHAT_IP = '130.237.67.115' # Furhat IP address
FURHAT_AGENT_NAME = 'system' # Furhat agent name. Can be found under "Connections" in the furhat web-GUI

# Print table
PRINT_FLAG = True

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

    class Interpreter(Process):
        """ The Interpreter-class is a intermediator between the arcitecture and learning module
        """
        def __init__(self):
            """ Constructor
            param: data_base_file [path]
            return: Interpreter [Process]
            """
            super(Interpreter, self).__init__()
            # Create a pipe to communicate to the client process
            self.pipe_in_client, self.pipe_out = os.pipe()
            self.pipe_in, self.pipe_out_client = os.pipe()

            # Create a client object to communicate with the server
            self.client = Client(client_type="interpreter",
                                 pipe_in=self.pipe_in_client,
                                 pipe_out=self.pipe_out_client)
            self.client.start()

            # Read the label file into a list of lists
            data_file = "../../logs/label_sequence.csv"
            with open(data_file, newline='') as csvfile:
                label_sequence = list(csv.reader(csvfile, delimiter=";"))
            self.label_sequence = []
            for row in label_sequence:
                self.label_sequence.append([int(lbl) for lbl in row])

            # Create and initialize the variables
            self.print_every = 1.0

            self.verb_keys = ["P1N", "P1A", "P1V", "P1D", "P1P", "P1F", "P1ASR", "P1Keywords", "P2N", "P2A", "P2V", "P2D", "P2P", "P2F", "P2ASR", "P2Keywords"]
            self.gaze_keys = ["P1GL", "P2GL", "P1HL", "P2HL", "P1PL", "P2PL", "P1HDL", "P2HDL"]

            self.current_step = 0
            self.attention_table = self._new_attention_table()
            self.current_verbal_dict = self._new_verbal_dict()
            self.verbal_table = {}

        def _new_attention_table(self):
            """ Create and return a new attention table.
            """
            att_table = {}
            att_attr = ["P1GL", "P2GL", "P1HL", "P2HL", "P1PL", "P2PL", "P1HDL", "P2HDL"]
            try:
                for i, label in enumerate(self.label_sequence[self.current_step]):
                    object_dict = {"L":label}
                    for key in att_attr:
                        object_dict[key] = 0

                    # Define objects. On lable sequence: P1, P2, F, T1-14
                    if i == 0:
                        att_table["P1"] = object_dict
                    elif i == 1:
                        att_table["P2"] = object_dict
                    elif i == 2:
                        att_table["Furhat"] = object_dict
                    else:
                        att_table["T{}".format(i-2)] = object_dict
                return att_table
            except IndexError:
                return False

        def _new_verbal_dict(self):
            """ Return a new verbal dictionary which consists only of the current time step int.
            """
            return {"step":self.current_step}

        def run(self):
            """ Main loop. Simply read messages from the server and send them to self._parse() to take
            appropriate action.
            param: N/A
            return: N/A
            """
            # Print attention table
            if PRINT_FLAG: self._print_blocks()

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
                            print("Disconnected from server")
                            sys.exit()
                        else:
                            self._parse(data.decode("utf-8"))

        def _parse(self, data):
            """ Interperet the incomming message and take appropriate action.
            param: data [String, format defined in README.md]
            return: N/A
            """
            # Preporcess the data message.
            data = data.replace("$", "")
            data = data.split(";")
            for i in range(1, len(data)):
                try:
                    data[i] = ast.literal_eval(data[i])
                except SyntaxError:
                    return
            if data[0] == "data":
                self._process(data)
            else:
                print("Unknown message type: {}".format(data[0]))

        def _process(self, data):
            data = data[1]

            # Save the data to the logfile
            self._do_log(data)

            # Process the verbal information in the data
            self._process_verbal(data)

            # Process the gaze and pointing information in the data
            self._process_gaze_hold(data)

            # Process input data online
            #print(data)

            # Check whether the message indicates end of step. If so then save the current state and
            # reset variables.
            if "S" in data.keys():
                self._do_step()

        def _do_log(self, data):
            log_msg = [str(data["TS"]), str(self.current_step)]
            del data["TS"]
            log_msg.append(str(data))
            self._save_as(log_msg, "../../logs/feature_log.csv")

        def _process_verbal(self, data):
            """ Add the verbal information in the verbal table.
            """
            data_keys = data.keys()
            for key in self.verb_keys:
                if key in data_keys:
                    try:
                        self.current_verbal_dict[key] += data[key]
                    except KeyError:
                        self.current_verbal_dict[key] = data[key]

        def _process_gaze_hold(self, data):
            """ Add the gaze information in the attention table.
            """
            for key in self.gaze_keys:
                try:
                    for value in data[key]:
                        self.attention_table[value][key] += 1
                except KeyError:
                    pass

        def _do_step(self):
            """ Save the current information and reset the variables.
            """
            # Format the attention table (dict) into a list of lists and save it.
            att_list = self._dict_of_dicts_to_list_of_lists(self.attention_table,
                                                            ['L'] + self.gaze_keys)
            self._save_as(att_list, "../../logs/attention_table_{}.csv".format(self.current_step))

            # Add the verbal information to the verbal_table.
            self.verbal_table[self.current_step] = self.current_verbal_dict

            # Increase the step counter and reset the variables.
            self.current_step += 1
            self.attention_table = self._new_attention_table()
            self.current_verbal_dict = self._new_verbal_dict()
            # If the attention_table returns false the label_sequence is empty and the program should
            # save and exit.
            if not self.attention_table:
                ver_list = self._dict_of_dicts_to_list_of_lists(self.verbal_table,
                                                                self.verb_keys)
                ver_list[0][0] = "Step"
                self._save_as(ver_list, "../../logs/language_table.csv")
                self.client.close()
                sys.exit()

        def _dict_of_dicts_to_list_of_lists(self, dict_of_dicts, keys):
            list_of_lists = []
            list_of_lists.append([self.current_step] + keys)
            for key, value in collections.OrderedDict(sorted(dict_of_dicts.items())).items():
                val = []
                for k in keys:
                    try:
                        val.append(str(value[k]))
                    except KeyError:
                        pass
                list_of_lists.append([key] + val)
            return list_of_lists

        def _save_as(self, data, file_name):
            with open(file_name, 'a') as data_file:
                writer = csv.writer(data_file, delimiter=';')
                if isinstance(data[0], list):
                    writer.writerows(data)
                else:
                    writer.writerow(data)

        def _print_blocks(self):
            threading.Timer(self.print_every, self._print_blocks).start()
            clear = "\n" * 100
            print(clear)
            print("_"*124)
            if self.attention_table:
                # Format the attention table (dict) into a list of lists and print it.
                att_list = self._dict_of_dicts_to_list_of_lists(self.attention_table,
                                                                ['L'] + self.gaze_keys)
                for row in att_list:
                    row_str = ""
                    for cell in row:
                        row_str += "{:<11}".format(cell)
                    print(row_str)
            print("_"*124)
