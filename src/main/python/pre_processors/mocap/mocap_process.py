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
mocap_dict[0]['name'] = 'target1'
mocap_dict[1]['name'] = 'target2'
mocap_dict[2]['name'] = 'target3'
# blue = glasses2
mocap_dict[3]['name'] = 'glasses2'

# Procees input data
def callback(_mq, get_shifted_time, routing_key, body):
    print('Connected! Receiving messages.')

    context = zmq.Context()
    s = context.socket(zmq.SUB)
    s.setsockopt_string(zmq.SUBSCRIBE, u'')
    s.connect(body.get('address'))

    while True:
        data = s.recv()
        msgdata, timestamp = msgpack.unpackb(data, use_list=False)

        # Get frame
        frame = msgdata['frameno']
        if DEBUG:
            print("----------------------------------------------------------------")
            print("Frame: ", frame)

        # Check how many objects
        objects = msgdata['sets']
        if DEBUG:
            for key in objects.keys():
                print("Object: ", key)

        # Get rigid bodies
        rigidbodies = msgdata['rigid_bodies']
        for count in range(0, len(rigidbodies)):
            # Take each rigid body
            rigidbody = rigidbodies[count]

            mocap_dict[count]['id'] = rigidbody[0]
            mocap_dict[count]['position'] = rigidbody[1]
            mocap_dict[count]['rotation'] = rigidbody[2]
            mocap_dict[count]['marker1'] = rigidbody[3][0]
            mocap_dict[count]['marker2'] = rigidbody[3][1]
            mocap_dict[count]['marker3'] = rigidbody[3][2]
            mocap_dict[count]['marker4'] = rigidbody[3][3]

            if DEBUG: print("Rigid body: ", mocap_dict[count])

        # Get timestamp
        mocaptimestamp = msgdata['timestamp']
        if DEBUG: print("Mocap timestamp: ", mocaptimestamp)

        # Send one by one the rigid body json files
        def sendjson(objectid):
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
                "id": mocap_dict[objectid]['id'],
                "name": mocap_dict[objectid]['name'],
                "position": poscoordtofloat(str(mocap_dict[objectid]['position'])),
                "rotation": rotcoordtofloat(str(mocap_dict[objectid]['rotation'])),
                "marker1": poscoordtofloat(str(mocap_dict[objectid]['marker1'])),
                "marker2": poscoordtofloat(str(mocap_dict[objectid]['marker2'])),
                "marker3": poscoordtofloat(str(mocap_dict[objectid]['marker3'])),
                "marker4": poscoordtofloat(str(mocap_dict[objectid]['marker4'])),
                "timestamp": mocaptimestamp
            }

            key = settings['messaging']['mocap_processing']
            new_routing_key = "{key}.{objname}".format(key=key, objname=mocap_dict[objectid]['name'])
            _mq.publish(exchange='pre-processor', routing_key=new_routing_key, body=json_data)

            return;

        # Send for every rigid body
        sendjson(0)
        sendjson(1)
        sendjson(2)
        sendjson(3)
    s.close()

mq = MessageQueue('mocap-preprocessor')
mq.bind_queue(exchange='sensors', routing_key=settings['messaging']['new_sensor_mocap'], callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
