import zmq
import sys
sys.path.append('..')
from shared import MessageQueue, resend_new_sensor_messages
from threading import Thread

mq = MessageQueue('zmq-server-keeper')

connections = {}

def callback(_mq, get_shifted_time, routing_key, body):
    splitted_key = routing_key.split('.')
    if len(splitted_key) > 1:
        if routing_key.split('.')[1] == 'new_sensor':
            # save the routing key into the dict, e.g. microphone.new_sensor.blue
            connections[routing_key] = body
    else:
        if routing_key.split('.')[1] == 'disconnected_sensor' and connections.get(routing_key):
            del connections[routing_key.replace('disconnected_sensor', 'new_sensor')]

mq.bind_queue(exchange='sensors', routing_key="*.new_sensor.*", callback=callback)
mq.bind_queue(exchange='sensors', routing_key="*.disconnected_sensor.*", callback=callback)


def zmq_connection(_mq):
    context = zmq.Context()
    s = context.socket(zmq.REP)
    s.bind('tcp://*:45322')
    while True:
        message = s.recv_string()
        s.send(b'')
        for routing_key, body in connections.items():
            if str(message) in routing_key:
                _mq.publish(exchange='sensors', routing_key=routing_key, body=body)


thread = Thread(target = zmq_connection, args=(mq, ))
thread.deamon = True
thread.start()


print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
