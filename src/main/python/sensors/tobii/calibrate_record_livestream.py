# Part of code here has been reused from Tobii API examples

import urllib2
import json
import time
import threading
import socket

GLASSES_IP = "192.168.0.113"  # IPv4 address
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

if __name__ == "__main__":
    global running
    running = True
    peer = (GLASSES_IP, PORT)

    try:
        # Create socket which will send a keep alive message for the live data stream
        data_socket = mksock(peer)
        td = threading.Timer(0, send_keepalive_msg, [data_socket, KA_DATA_MSG, peer])
        td.start()
        print "Data socket created"

        # Create socket which will send a keep alive message for the live video stream
        video_socket = mksock(peer)
        tv = threading.Timer(0, send_keepalive_msg, [video_socket, KA_VIDEO_MSG, peer])
        tv.start()
        print "Video socket created"

        project_id = create_project()
        print "Project created", project_id
        participant_id = create_participant(project_id)
        print "Participant created", participant_id
        calibration_id = create_calibration(project_id, participant_id)
        print "Calibration created", calibration_id

        print "Project: " + project_id, ", Participant: ", participant_id, ", Calibration: ", calibration_id, " "

        input_var = raw_input("Press enter to calibrate")
        print ('Calibration started...')
        start_calibration(calibration_id)
        status = wait_for_status('/api/calibrations/' + calibration_id + '/status', 'ca_state', ['failed', 'calibrated'])

        if status == 'failed':
            print ('Calibration failed, using default calibration instead')
        else:
            print ('Calibration successful')

        recording_id = create_recording(participant_id)
        print ('Recording started...')
        start_recording(recording_id)

        # Get livestreamed data
        while True:
            # Read live data
            data, address = data_socket.recvfrom(1024)
            print (data)

    finally:
        # Stop recording
        stop_recording(recording_id)
        print "Recording Stopped"

        # Check recording status
        status = wait_for_status('/api/recordings/' + recording_id + '/status', 'rec_state', ['failed', 'done'])
        if status == 'failed':
            print ('Recording failed')
        else:
            print ('Recording successful')

        print "Press ctr+z to exit."

    running = False
