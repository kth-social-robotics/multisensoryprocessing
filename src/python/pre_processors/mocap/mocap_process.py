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

DEBUG = False

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Dictionaries
mocap_dict = defaultdict(lambda : defaultdict(dict))
# white = glasses1
mocap_dict['white']['type'] = 'glasses'
# pink = kinnect1
mocap_dict['pink']['type'] = 'hat'
# blue = glasses2
mocap_dict['blue']['type'] = 'glasses'
# orange = kinnect2
mocap_dict['orange']['type'] = 'hat'
# brown = glasses3
mocap_dict['brown']['type'] = 'glasses'
# black = kinnect3
mocap_dict['black']['type'] = 'hat'

# Procees input data
def callback(_mq, get_shifted_time, routing_key, body):
    print('Connected! Sending messages.')

    context = zmq.Context()
    s = context.socket(zmq.SUB)
    s.setsockopt_string(zmq.SUBSCRIBE, u'')
    s.connect(body.get('address'))

    # Initiate parameters
    frame = None
    objects = None
    name = None
    pname = None
    position = None
    rotation = None
    marker0 = None
    marker0name = None
    marker0pos = None
    marker1 = None
    marker1name = None
    marker1pos = None
    marker2 = None
    marker2name = None
    marker2pos = None
    marker3 = None
    marker3name = None
    marker3pos = None

    while True:
        data = s.recv()
        msgdata_list, timestamp = msgpack.unpackb(data, use_list=False)

        for msgdata in msgdata_list:
            # Get frame
            r0 = re.search('Frame Number: (.*)', msgdata)
            if r0:
                frames = r0.group(1)
                if frames != '0':
                    frame = frames
                    if DEBUG:
                        print("----------------------------------------------------------------")
                        print("Frame: ", frame)

            # Check how many objects
            #r1 = re.search('Subjects (.+?):', msgdata)
            #if r1:
                #objects = r1.group(1)
                #objects = objects[1]
                #print("Objects: ", objects)

            # Get Object No
            r2 = re.search('Subject #(.*)', msgdata)
            if r2:
                objectno = r2.group(1)
                if DEBUG: print("Object: ", objectno)

            # Get Object name
            r3 = re.search('Root Segment: (.*)', msgdata)
            if r3:
                name = r3.group(1)
                if DEBUG: print("Name: ", name)

                r3a = re.search('_(.*)', msgdata)
                if r3a:
                    pname = r3a.group(1)
                    if DEBUG: print("Participant Name: ", pname)
                mocap_dict[pname]['participant'] = pname
                mocap_dict[pname]['object'] = name

            # Get object position
            r4 = re.search('Global Translation: (.+?) False', msgdata)
            if r4:
                position = r4.group(1)
                if DEBUG: print("Position: ", position)
                mocap_dict[pname]['position'] = position

            # Get object rotation
            r5 = re.search('Global Rotation Quaternion: (.+?) False', msgdata)
            if r5:
                rotation = r5.group(1)
                if DEBUG: print("Rotation: ", rotation)
                mocap_dict[pname]['rotation'] = rotation

            # Get marker 0 position
            r6 = re.search('Marker #0: (.+?) False', msgdata)
            if r6:
                marker0 = r6.group(1)
                # Get marker 0 name
                r6a = re.search('(.*) \(.*\)', marker0)
                if r6a:
                    marker0name = r6a.group(1)
                    if DEBUG: print("Marker 0 Name: ", marker0name)
                # Get marker 0 position
                marker0pos = re.search(r'\((.*?)\)', marker0).group(1)
                if DEBUG: print("Marker 0 Position: ", marker0pos)
                mocap_dict[pname]['marker0name'] = marker0name
                mocap_dict[pname]['marker0pos'] = marker0pos

            # Get marker 1 position
            r7 = re.search('Marker #1: (.+?) False', msgdata)
            if r7:
                marker1 = r7.group(1)
                # Get marker 1 name
                r7a = re.search('(.*) \(.*\)', marker1)
                if r7a:
                    marker1name = r7a.group(1)
                    if DEBUG: print("Marker 1 Name: ", marker1name)
                # Get marker 1 position
                marker1pos = re.search(r'\((.*?)\)', marker1).group(1)
                if DEBUG: print("Marker 1 Position: ", marker1pos)
                mocap_dict[pname]['marker1name'] = marker1name
                mocap_dict[pname]['marker1pos'] = marker1pos

            # Get marker 2 position
            r8 = re.search('Marker #2: (.+?) False', msgdata)
            if r8:
                marker2 = r8.group(1)
                # Get marker 2 name
                r8a = re.search('(.*) \(.*\)', marker2)
                if r8a:
                    marker2name = r8a.group(1)
                    if DEBUG: print("Marker 2 Name: ", marker2name)
                # Get marker 2 position
                marker2pos = re.search(r'\((.*?)\)', marker2).group(1)
                if DEBUG: print("Marker 2 Position: ", marker2pos)
                mocap_dict[pname]['marker2name'] = marker2name
                mocap_dict[pname]['marker2pos'] = marker2pos

            # Get marker 3 position
            r9 = re.search('Marker #3: (.+?) False', msgdata)
            if r9:
                marker3 = r9.group(1)
                # Get marker 3 name
                r9a = re.search('(.*) \(.*\)', marker3)
                if r9a:
                    marker3name = r9a.group(1)
                    if DEBUG: print("Marker 3 Name: ", marker3name)
                # Get marker 3 position
                marker3pos = re.search(r'\((.*?)\)', marker3).group(1)
                if DEBUG: print("Marker 3 Position: ", marker3pos)
                mocap_dict[pname]['marker3name'] = marker3name
                mocap_dict[pname]['marker3pos'] = marker3pos

            # Send processed data
            r10 = re.search('Waiting for new frame...', msgdata)
            if r10 and all(mocap_dict[pname].values()):
                # Send one by one the participant json files
                def sendjson(participantname):
                    # Parse coordinates to float
                    def poscoordtofloat(coord):
                        if coord and coord != '0':
                            x, y, z = map(float, coord[1:][:-1].split(", "))
                            return {"x": x, "y": y, "z": z}
                        else:
                            return None
                    def rotcoordtofloat(coord):
                        if coord and coord != '0':
                            x, y, z, w = map(float, coord[1:][:-1].split(", "))
                            return {"x": x, "y": y, "z": z, "w": w}
                        else:
                            return None

                    json_data = {
                    	"frame": frame,
                    	"participant": mocap_dict[participantname]['participant'],
                    	"coord": "xyz_left",
                    	"head": {
                    		"type": mocap_dict[participantname]['type'],
                    		"name":  mocap_dict[participantname]['object'],
                    		"position": poscoordtofloat(mocap_dict[participantname]['position']),
                    		"rotation": rotcoordtofloat(mocap_dict[participantname]['rotation']),
                    		"markers":
                    		[
                    			{
                    				"name": mocap_dict[participantname]['marker0name'],
                    				"position": poscoordtofloat(mocap_dict[participantname]['marker0pos'])
                    			},
                    			{
                    				"name": mocap_dict[participantname]['marker1name'],
                    				"position": poscoordtofloat(mocap_dict[participantname]['marker1pos'])
                    			},
                    			{
                    				"name": mocap_dict[participantname]['marker2name'],
                    				"position": poscoordtofloat(mocap_dict[participantname]['marker2pos'])
                    			},
                    			{
                    				"name": mocap_dict[participantname]['marker3name'],
                    				"position": poscoordtofloat(mocap_dict[participantname]['marker3pos'])
                    			}
                    		]
                    	},
                    	"glove_left": {},
                    	"glove_right": {}
                    }

                    key = settings['messaging']['mocap_processing']
                    new_routing_key = "{key}.{participant}".format(key=key, participant=participantname)
                    _mq.publish(exchange='pre-processor', routing_key=new_routing_key, body=json_data)

                    return;

                # Send for every participant
                sendjson('white')
                sendjson('pink')
                sendjson('blue')
                sendjson('orange')
                sendjson('brown')
                sendjson('black')
    s.close()

mq = MessageQueue('mocap-preprocessor')
mq.bind_queue(exchange='sensors', routing_key=settings['messaging']['new_sensor_mocap'], callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
