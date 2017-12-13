# python mocap_process.py

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
from shared import create_zmq_server, MessageQueue

DEBUG = False

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Define server
zmq_socket, zmq_server_addr = create_zmq_server()
mq = MessageQueue('mocap-preprocessor')

mq.publish(
    exchange='pre-processor',
    routing_key=settings['messaging']['mocap_processing'],
    body={'address': zmq_server_addr, 'file_type': 'txt'}
)

# Dictionaries
mocap_dict = defaultdict(lambda : defaultdict(dict))
mocap_dict[0]['name'] = 'glasses1'
mocap_dict[1]['name'] = 'hand1l'
mocap_dict[2]['name'] = 'hand1r'
mocap_dict[3]['name'] = 'target1'
mocap_dict[4]['name'] = 'target2'
mocap_dict[5]['name'] = 'table1'

# Procees input data
def callback(_mq, get_shifted_time, routing_key, body):
    print('Connected! Receiving messages.')

    context = zmq.Context()
    s = context.socket(zmq.SUB)
    s.setsockopt_string(zmq.SUBSCRIBE, u'')
    s.connect(body.get('address'))

    while True:
        data = s.recv()
        msgdata, localtime = msgpack.unpackb(data, use_list=False)

        # Get frame
        frame = msgdata['frameno']
        if DEBUG:
            print("----------------------------------------------------------------")
            print("Frame: ", frame)

        # Get objects
        objects = msgdata['sets']

        if DEBUG:
            for key in objects.keys():
                if key != 'all':
                    print("Object: ", key)

        # Get rigid bodies
        rigidbodies = msgdata['rigid_bodies']
        for count in range(0, len(rigidbodies)):
            # Take each rigid body
            rigidbody = rigidbodies[count]

            # Check that marker 1 position is the same in sets and rigidbodies
            if objects['glasses1'][0] == rigidbody[3][0]:
                objid = 0
            elif objects['hand1l'][0] == rigidbody[3][0]:
                objid = 1
            elif objects['hand1r'][0] == rigidbody[3][0]:
                objid = 2
            elif objects['target1'][0] == rigidbody[3][0]:
                objid = 3
            elif objects['target2'][0] == rigidbody[3][0]:
                objid = 4
            elif objects['table1'][0] == rigidbody[3][0]:
                objid = 5

            mocap_dict[objid]['id'] = rigidbody[0]
            mocap_dict[objid]['position'] = rigidbody[1]
            mocap_dict[objid]['rotation'] = rigidbody[2]
            mocap_dict[objid]['marker1'] = rigidbody[3][0]
            mocap_dict[objid]['marker2'] = rigidbody[3][1]
            mocap_dict[objid]['marker3'] = rigidbody[3][2]
            mocap_dict[objid]['marker4'] = rigidbody[3][3]

            if DEBUG: print("Rigid body: ", mocap_dict[objid])

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
                "mocaptimestamp": mocaptimestamp,
                "localtime": localtime
            }

            # key = settings['messaging']['mocap_processing']
            # new_routing_key = "{key}.{objname}".format(key=key, objname=mocap_dict[objectid]['name'])
            # _mq.publish(exchange='pre-processor', routing_key=new_routing_key, body=json_data)

            zmq_socket.send(msgpack.packb((json_data, mq.get_shifted_time())))

            return;

        # Send for every rigid body
        sendjson(0)
        sendjson(1)
        sendjson(2)
        sendjson(3)
        sendjson(4)
        sendjson(5)
    s.close()

mq = MessageQueue('mocap-preprocessor')
mq.bind_queue(exchange='sensors', routing_key=settings['messaging']['new_sensor_mocap'], callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()

zmq_socket.send(b'CLOSE')
zmq_socket.close()
