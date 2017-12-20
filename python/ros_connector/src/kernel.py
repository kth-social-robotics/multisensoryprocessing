import subprocess
import time
from os.path import dirname, join, realpath

from .interpreter import Interpreter
from .logger import Logger
from .server import Server
from .dummies import ArchitectureDummy
from .dummies import YuMiDummy

class Kernel(object):
    def __init__(self, commands):
        """ Initialize the TCP/IP server, ROS subscriber and the parser. 
        """
        logger = Logger()
        logger.start()
        if commands["server"]:
            self.server = Server(log_queue=logger.queue)
        if commands["interpreter"]:
            self.interpreter = Interpreter(log_queue=logger.queue)
        if commands["architecture_dummy"]:
            self.architecture_dummy = ArchitectureDummy()
        if commands["yumi_dummy"]:
            self.yumi_dummy = YuMiDummy()

        self.commands = commands
    
    def run(self):
        if self.commands["server"]:
            self.server.start()
            # Wait a second so that the server is up before the other processes starts.
            time.sleep(1)
        if self.commands["interpreter"]:
            self.interpreter.start()
        if self.commands["architecture_dummy"]:
            self.architecture_dummy.start()
        if self.commands["yumi_dummy"]:
            self.yumi_dummy.start()
        if self.commands["subscriber"]:
            subprocess.call((['python2.7', join(dirname(realpath(__file__)), "subscriber.py")]))
