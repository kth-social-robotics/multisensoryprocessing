# Get access to tobii live video streaming: rtsp://130.237.67.216:8554/live/eyes or scene
# websocketd --port=8080 python2 mocap_gaze.py 1 25
# Start webgl: http://130.237.67.190:8888/webgl/realtimevis/realtime/vs.html?IP=130.237.67.190
# python2 mocap_gaze.py 2 25
# py -2 .\mocap_gaze.py 2 25
# Check number of mocap objects
# Wait for Matlab to start

import zmq
import pika
import json
import time
import msgpack
import re
import sys
sys.path.append('../..')
from shared import MessageQueue
import yaml
from collections import defaultdict
import math
from shared import create_zmq_server, MessageQueue
from threading import Thread
import matlab.engine
from furhat import connect_to_iristk
from time import sleep

FURHAT_IP = '130.237.67.115' # Furhat IP address
FURHAT_AGENT_NAME = 'system' # Furhat agent name. Can be found under "Connections" in the furhat web-GUI

# Get print flag
if len(sys.argv) != 3:
    exit('Error. Enter print flag and number of objects')
printflag = sys.argv[1]
objectnum = sys.argv[2]

# Start matlab engine
mateng = matlab.engine.start_matlab()
#mateng.addpath(r'/Users/diko/Dropbox/University/PhD/Code/MultiSensoryProcessing/multisensoryprocessing/matlab', nargout=0)
mateng.addpath(r'C:/Users/PMIL/Documents/GitHub/multisensoryprocessing/matlab', nargout=0)
print("MATLAB")

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Define server
zmq_socket, zmq_server_addr = create_zmq_server()
mq = MessageQueue('mocaptobii-processor')

mq.publish(
    exchange='processor',
    routing_key=settings['messaging']['mocaptobii_processing'],
    body={'address': zmq_server_addr, 'file_type': 'txt'}
)

# Dictionaries
tobiimocap_dict = defaultdict(lambda : defaultdict(dict))

# Each key is the local timestamp in seconds. The second key is the frame
tobiimocap_dict[0][0]['device'] = 'body'

# Connect to Furhat
with connect_to_iristk(FURHAT_IP) as furhat_client:
    # Introduce Furhat
    furhat_client.say(FURHAT_AGENT_NAME, 'Now please help my friend to calibrate my vision.')
    furhat_client.gaze(FURHAT_AGENT_NAME, {'x':3.00,'y':0.00,'z':2.00}) # At default P1 position
    #furhat_client.gaze(FURHAT_AGENT_NAME, {'x':-2.00,'y':0.00,'z':2.00}) # At default P2 position

    # Log Furhat events
    def event_callback(event):
        #print(event) # Receives each event the furhat sends out.
        fd = open('../../../logs/furhat_log.csv','a')
        fd.write(event)
        fd.write('\n')
        fd.close()

    # Listen to events
    furhat_client.start_listening(event_callback) # register the event callback receiver

    # Procees mocap input data
    def mocapcallback(_mq1, get_shifted_time1, routing_key1, body1):
        context1 = zmq.Context()
        s1 = context1.socket(zmq.SUB)
        s1.setsockopt_string(zmq.SUBSCRIBE, u'')
        s1.connect(body1.get('address'))

        def runA():
            while True:
                data1 = s1.recv()
                mocapbody, localtime1 = msgpack.unpackb(data1, use_list=False)

                # Get mocap localtime
                mocaptime = mocapbody['localtime']

                # First get which second
                second = int(mocaptime)

                # Get decimals to decide which frame
                frame = int(math.modf(mocaptime)[0] * 50)

                # Put in dictionary
                tobiimocap_dict[second][frame]['mocap_' + mocapbody['name']] = mocapbody

                # Check that all mocap objects have arrived
                if (len(tobiimocap_dict[second][frame]) == int(objectnum)):
                    # Get gaze values from the 10th previous frame
                    if frame < 10:
                        new_second = second - 1
                        new_frame = frame + 40
                    else:
                        new_second = second
                        new_frame = frame - 10

                    def mocapgaze(tobii_device, mocap_device):
                        # Get values from json
                        gp3 = matlab.double([tobiimocap_dict[new_second][new_frame][tobii_device]['gp3']['x'], tobiimocap_dict[new_second][new_frame][tobii_device]['gp3']['y'], tobiimocap_dict[new_second][new_frame][tobii_device]['gp3']['z']])
                        pos = matlab.double([tobiimocap_dict[new_second][new_frame][mocap_device]['position']['x'], tobiimocap_dict[new_second][new_frame][mocap_device]['position']['y'], tobiimocap_dict[new_second][new_frame][mocap_device]['position']['z']])
                        quat = matlab.double([tobiimocap_dict[new_second][new_frame][mocap_device]['rotation']['x'], tobiimocap_dict[new_second][new_frame][mocap_device]['rotation']['y'], tobiimocap_dict[new_second][new_frame][mocap_device]['rotation']['z'], tobiimocap_dict[new_second][new_frame][mocap_device]['rotation']['w']])
                        rgbMarkers = matlab.double([[[tobiimocap_dict[new_second][new_frame][mocap_device]['marker1']['x'], tobiimocap_dict[new_second][new_frame][mocap_device]['marker2']['x'], tobiimocap_dict[new_second][new_frame][mocap_device]['marker3']['x'], tobiimocap_dict[new_second][new_frame][mocap_device]['marker4']['x']], [tobiimocap_dict[new_second][new_frame][mocap_device]['marker1']['y'], tobiimocap_dict[new_second][new_frame][mocap_device]['marker2']['y'], tobiimocap_dict[new_second][new_frame][mocap_device]['marker3']['y'], tobiimocap_dict[new_second][new_frame][mocap_device]['marker4']['y']], [tobiimocap_dict[new_second][new_frame][mocap_device]['marker1']['z'], tobiimocap_dict[new_second][new_frame][mocap_device]['marker2']['z'], tobiimocap_dict[new_second][new_frame][mocap_device]['marker3']['z'], tobiimocap_dict[new_second][new_frame][mocap_device]['marker4']['z']]]]) # [x1, x2, x3], [y1, y2, y3], [z1, z2, z3]

                        # Combine mocap and gaze. GP3 in mocap space (in Matlab)
                        gp3_3d = mateng.mocapgaze(tobii_device, gp3, pos, quat, rgbMarkers)

                        # Get 3d values
                        gaze_left = {"x": gp3_3d[0][0][0], "y": gp3_3d[0][1][0], "z": gp3_3d[0][2][0]}
                        gaze_right = {"x": gp3_3d[0][0][1], "y": gp3_3d[0][1][1], "z": gp3_3d[0][2][1]}
                        gaze_gp3 = {"x": gp3_3d[0][0][2], "y": gp3_3d[0][1][2], "z": gp3_3d[0][2][2]}
                        head_pose = {"x": gp3_3d[0][0][3], "y": gp3_3d[0][1][3], "z": gp3_3d[0][2][3]}

                        # Update dict values
                        tobiimocap_dict[new_second][new_frame][tobii_device]['gp3_3d'] = gaze_gp3
                        tobiimocap_dict[new_second][new_frame][tobii_device]['headpose'] = head_pose

                    # Check that the frame exists
                    if tobiimocap_dict[new_second][new_frame]:
                        # Run for tobii 1
                        if 'tobii_glasses1' in tobiimocap_dict[new_second][new_frame] and 'mocap_glasses1' in tobiimocap_dict[new_second][new_frame]:
                            mocapgaze('tobii_glasses1', 'mocap_glasses1')
                        # Run for tobii 2
                        if 'tobii_glasses2' in tobiimocap_dict[new_second][new_frame] and 'mocap_glasses2' in tobiimocap_dict[new_second][new_frame]:
                            mocapgaze('tobii_glasses2', 'mocap_glasses2')
                        # Run for tobii 3
                        if 'tobii_glasses3' in tobiimocap_dict[new_second][new_frame] and 'mocap_glasses3' in tobiimocap_dict[new_second][new_frame]:
                            mocapgaze('tobii_glasses3', 'mocap_glasses3')

                    # Print and send 10 frames before
                    # Send to WebGL
                    if printflag == '1':
                        # Only send every 2 frames
                        if frame % 2 == 0: # odd frames
                            print(tobiimocap_dict[new_second][new_frame])
                    zmq_socket.send(msgpack.packb((tobiimocap_dict[new_second][new_frame], mq.get_shifted_time())))

                    # Remove from dictionary
                    tobiimocap_dict[new_second].pop(new_frame, None)

                    #key = settings['messaging']['mocaptobii_processing']
                    #_mq.publish(exchange='processor', routing_key=key, body=tobiimocap_dict[new_second][new_frame])

        t1 = Thread(target = runA)
        t1.setDaemon(True)
        t1.start()
        #s1.close()

    # Procees tobii input data
    def tobiicallback(_mq2, get_shifted_time2, routing_key2, body2):
        context2 = zmq.Context()
        s2 = context2.socket(zmq.SUB)
        s2.setsockopt_string(zmq.SUBSCRIBE, u'')
        s2.connect(body2.get('address'))

        def runB():
            while True:
                data2 = s2.recv()
                tobiibody, localtime2 = msgpack.unpackb(data2, use_list=False)

                # Get tobii localtime
                tobiitime = tobiibody['localtime']

                # First get which second
                second = int(tobiitime)

                # Get decimals to decide which frame
                frame = int(math.modf(tobiitime)[0] * 50)

                # Put in dictionary
                tobiimocap_dict[second][frame]['tobii_' + tobiibody['name']] = tobiibody

        t2 = Thread(target = runB)
        t2.setDaemon(True)
        t2.start()
        #s2.close()

    mq = MessageQueue('mocaptobii-processor')
    mq.bind_queue(exchange='pre-processor', routing_key=settings['messaging']['mocap_processing'], callback=mocapcallback)
    mq.bind_queue(exchange='pre-processor', routing_key=settings['messaging']['tobii_processing'], callback=tobiicallback)

    mq.listen()

    zmq_socket.send(b'CLOSE')
    zmq_socket.close()
