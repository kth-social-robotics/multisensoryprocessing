#/usr/bin/env python2.7

import os
import sys
import time
from multiprocessing import Process

import rospy
import trajectory_msgs.msg

from client import Client


class Subscriber(Process):
    def __init__(self):
        """ Constructor
        """
        super(Subscriber ,self).__init__()

        # Create a pipe to communicate to the client process
        self.pipe_in_client, self.pipe_out = os.pipe()
        self.pipe_in, self.pipe_out_client = os.pipe()
        # Create a client object to communicate with the server
        self.client = Client(client_type="subscriber",
                             pipe_in=self.pipe_in_client,
                             pipe_out=self.pipe_out_client)
        self.client.start() 
    
    def parse(self, data):
        """ Parsing trajectory data and sending it to hololens.
        """
        positions = [[str(position) for position in point.positions] for point in data.points]
        positions.insert(0, data.joint_names)
        positions = ";".join([",".join(position) for position in positions])
        positions = "hololens;trajectory;" + positions + "$"
        os.write(self.pipe_out, positions.encode("utf-8"))
        sys.stdout.flush()
        time.sleep(1)


    def run(self):
        """ Main loop
        """
        rospy.init_node('listener', anonymous=True)
        rospy.Subscriber("/yumi/traj_moveit", trajectory_msgs.msg.JointTrajectory, self.parse)
        rospy.spin()

if __name__ == "__main__":
    subscriber = Subscriber()
    subscriber.run()
