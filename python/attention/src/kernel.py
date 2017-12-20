import subprocess
import time
from os.path import dirname, join, realpath

from .interpreter import Interpreter
from .logger import Logger
from .server import Server
from .dummies import ArchitectureDummy

class Kernel(object):
    def __init__(self, commands):
        """ Initialize the TCP/IP server, ROS subscriber and the parser.
        """
        self.children = []
        if commands["server"]:
            self.children.append(Server())
        if commands["interpreter"]:
            self.children.append(Interpreter())
        if commands["architecture_dummy"]:
            self.children.append(ArchitectureDummy())

    def run(self):
        for child in self.children:
            child.start()
            time.sleep(0.5)
        for child in self.children:
            child.join()
