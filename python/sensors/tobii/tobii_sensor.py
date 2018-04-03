# py -2 tobii_sensor.py white 130.237.67.216 (glasses1)
# py -2 tobii_sensor.py blue 130.237.67.145 (glasses2)
# py -2 tobii_sensor.py brown 130.237.67.206 (glasses3)

import pika
import sys
import time
import msgpack
sys.path.append('../..')
from shared import create_zmq_server, MessageQueue
from subprocess import Popen, PIPE
import yaml
import urllib2
import json
import threading
import socket

# Get tobii address and participant
if len(sys.argv) != 3:
    exit('Error. python tobii_sensor.py')
participant = sys.argv[1]
ip = sys.argv[2]

# Settings
SETTINGS_FILE = '../../settings.yaml'

# Print messages
DEBUG = False

# Estabish la conneccion!
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Get tobii data stream
GLASSES_IP = ip #"192.168.0.113" # IPv4 address
PORT = 49152
base_url = 'http://' + GLASSES_IP
timeout = 1

# Keep-alive message content used to request live data and live video streams
KA_DATA_MSG = "{\"type\": \"live.data.unicast\", \"key\": \"some_GUID\", \"op\": \"start\"}"
KA_VIDEO_MSG = "{\"type\": \"live.video.unicast\", \"key\": \"some_other_GUID\", \"op\": \"start\"}"

# Create UDP socket
def mksock(peer):
    iptype = socket.AF_INET
    if ':' in peer[0]:
        iptype = socket.AF_INET6
    return socket.socket(iptype, socket.SOCK_DGRAM)

# Callback function
def send_keepalive_msg(socket, msg, peer):
    global running
    while running:
        socket.sendto(msg, peer)
        time.sleep(timeout)

def post_request(api_action, data=None):
    url = base_url + api_action
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(data)
    response = urllib2.urlopen(req, data)
    data = response.read()
    json_data = json.loads(data)
    return json_data

def wait_for_status(api_action, key, values):
    url = base_url + api_action
    running = True
    while running:
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(req, None)
        data = response.read()
        json_data = json.loads(data)
        if json_data[key] in values:
            running = False
        time.sleep(1)

    return json_data[key]

def create_project():
    json_data = post_request('/api/projects')
    return json_data['pr_id']

def create_participant(project_id):
    data = {'pa_project': project_id}
    json_data = post_request('/api/participants', data)
    return json_data['pa_id']

def create_calibration(project_id, participant_id):
    data = {'ca_project': project_id, 'ca_type': 'default', 'ca_participant': participant_id}
    json_data = post_request('/api/calibrations', data)
    return json_data['ca_id']

def start_calibration(calibration_id):
    post_request('/api/calibrations/' + calibration_id + '/start')

def create_recording(participant_id):
    data = {'rec_participant': participant_id}
    json_data = post_request('/api/recordings', data)
    return json_data['rec_id']

def start_recording(recording_id):
    post_request('/api/recordings/' + recording_id + '/start')

def stop_recording(recording_id):
    post_request('/api/recordings/' + recording_id + '/stop')

# Main
global running
running = True
peer = (GLASSES_IP, PORT)

try:
    # Create socket which will send a keep alive message for the live data stream
    data_socket = mksock(peer)
    td = threading.Timer(0, send_keepalive_msg, [data_socket, KA_DATA_MSG, peer])
    td.daemon = True
    td.start()
    print("Data socket created")

    # Create socket which will send a keep alive message for the live video stream
    video_socket = mksock(peer)
    tv = threading.Timer(0, send_keepalive_msg, [video_socket, KA_VIDEO_MSG, peer])
    tv.daemon = True
    tv.start()
    print("Video socket created")

    project_id = create_project()
    print("Project created", project_id)
    participant_id = create_participant(project_id)
    print("Participant created", participant_id)
    calibration_id = create_calibration(project_id, participant_id)
    print("Calibration created", calibration_id)

    print("Project: " + project_id, ", Participant: ", participant_id, ", Calibration: ", calibration_id, " ")

    input_var = raw_input("Press enter to calibrate")
    print('Calibration started...')
    start_calibration(calibration_id)
    status = wait_for_status('/api/calibrations/' + calibration_id + '/status', 'ca_state', ['failed', 'calibrated'])

    if status == 'failed':
        print('Calibration failed, using default calibration instead')
    else:
        print('Calibration successful')

    recording_id = create_recording(participant_id)
    print('Recording started...')
    start_recording(recording_id)

    # Define server
    zmq_socket, zmq_server_addr = create_zmq_server()
    mq = MessageQueue('tobii-sensor')

    # Check which participant
    routing_key_p = '{}.{}'.format(settings['messaging']['new_sensor_tobii'], participant)
    mq.publish(
        exchange='sensors',
        routing_key=routing_key_p,
        body={'address': zmq_server_addr, 'file_type': 'txt'}
    )

    print("Recording in progress...")

    # Init pack
    packed_data = []
    old_ts = 0

    # Get livestreamed data
    while True:
        # Read live data
        data, address = data_socket.recvfrom(1024)

        # Pack data by timestamp
        if all(True if bad_candidate not in data else False for bad_candidate in ['ac', 'gy', 'pts', 'vts']):
            new_ts = json.loads(data).get("ts")

            if packed_data and new_ts != old_ts:
                # Send data stream
                zmq_socket.send(msgpack.packb((packed_data, mq.get_shifted_time())))

                if DEBUG:
                    print(packed_data)
                    print('---------------------------------------')

                packed_data = []
                old_ts = new_ts
            elif not packed_data:
                old_ts = new_ts

            packed_data.append(data)

finally:
    # Stop recording
    stop_recording(recording_id)
    print("Recording stopped")

    # Check recording status
    status = wait_for_status('/api/recordings/' + recording_id + '/status', 'rec_state', ['failed', 'done'])
    if status == 'failed':
        print('Recording failed')
    else:
        print('Recording successful')

    # Send end of recording
    data = "END"
    zmq_socket.send(msgpack.packb((data, mq.get_shifted_time())))

    # Close la conneccion
    zmq_socket.send(b"CLOSE")
    zmq_socket.close()
    print("DONE")

running = False
