from datetime import datetime
from multiprocessing import Process, Queue
from threading import Thread

import msgpack
import msgpack_numpy as m

from farmi.farmi_unit import FarmiUnit

m.patch()
import time
import zmq


DIRECTORY_SERVICE_TOPICS_PORT = 5563
DIRECTORY_SERVICE_SUBSCRIBE_PORT = 5561


def listen_to_new_topics(que, topic, ip):
    context = zmq.Context()
    s2 = context.socket(zmq.SUB)
    s2.setsockopt(zmq.SUBSCRIBE, b'')
    s2.connect(f'tcp://{ip}:{DIRECTORY_SERVICE_SUBSCRIBE_PORT}')
    while True:
        data = s2.recv_json()
        if data.get(topic):
            que.put(data[topic])


def listen_on_subject(topic_address, que2, topic, sub_topic):
    context = zmq.Context()
    sub = context.socket(zmq.SUB)
    sub.setsockopt(zmq.SUBSCRIBE, b'')
    sub.connect(topic_address)
    while True:
        recv_topic, recv_sub_topic, recv_time, recv_d = sub.recv_multipart()
        if not sub_topic or sub_topic == '*' or recv_sub_topic == sub_topic:
            que2.put((recv_sub_topic.decode('utf-8'), recv_time.decode('utf-8'), msgpack.unpackb(recv_d, raw=False)))
   
       
def another_one(que, que2, topic, sub_topic):
    while True:
        data = que.get()
        Process(target=listen_on_subject, args=(data, que2, topic, sub_topic)).start()



def another_one_two(que, full_topic, directory_service_ip):
    topic, sub_topic = full_topic.rsplit('.', 1) if '.' in full_topic else full_topic, None

    context = zmq.Context()
    s = context.socket(zmq.REQ)
    s.connect(f'tcp://{directory_service_ip}:{DIRECTORY_SERVICE_TOPICS_PORT}')

    context = zmq.Context()
    s2 = context.socket(zmq.SUB)
    s2.setsockopt(zmq.SUBSCRIBE, b'')
    s2.connect(f'tcp://{directory_service_ip}:{DIRECTORY_SERVICE_SUBSCRIBE_PORT}')

    poller = zmq.Poller()
    poller.register(s2, zmq.POLLIN)

    time.sleep(1)
    s.send(b'')
    s.recv()
    current_topic_socket = None
    current_address = None

    while True:
        socks = dict(poller.poll())
        if s2 in socks:
            data = s2.recv_json()
            if data.get(topic) and current_address != data.get(topic):
                if current_topic_socket:
                    poller.unregister(current_topic_socket)
                    current_topic_socket.close()
                current_address = data[topic]
                current_topic_socket = context.socket(zmq.SUB)
                current_topic_socket.setsockopt(zmq.SUBSCRIBE, b'')
                current_topic_socket.connect(data[topic])
                poller.register(current_topic_socket, zmq.POLLIN)
        elif current_topic_socket in socks:
            recv_topic, recv_sub_topic, recv_time, recv_d = current_topic_socket.recv_multipart()
            if not sub_topic or sub_topic == '*' or recv_sub_topic == sub_topic:
                que.put((recv_sub_topic.decode('utf-8'), recv_time.decode('utf-8'), msgpack.unpackb(recv_d, raw=False)))

def register_farmi_callbacks(full_topic, callback, directory_service_ip='127.0.0.1'):

    q = Queue()
    # q2 = Queue()

    # Process(target=listen_to_new_topics, args=(q, topic, directory_service_ip)).start()
    # Process(target=another_one, args=(q, q2, topic, sub_topic)).start()
    Thread(target=another_one_two, args=(q, full_topic, directory_service_ip)).start()

    while True:
        callback(*q.get())


def farmi(subscribe=None, publish=None, send_pyobj=False, local_save=False, directory_service_ip='127.0.0.1'):
    def outer_wrapper(func):
        def inner_wrapper(*args, **kwargs):
            if publish:
                pub = FarmiUnit(publish, send_pyobj, local_save=local_save)

            def handle_callback(topic, time, data):
                if publish:
                    func(pub, topic, time, data, *args, **kwargs)
                else:
                    func(topic, time, data, *args, **kwargs)

            if subscribe:
                register_farmi_callbacks(subscribe, handle_callback, directory_service_ip=directory_service_ip)
            elif publish:
                func(pub, *args, **kwargs)
            else:
                func(*args, **kwargs)

            if publish:
                pub.close()
        return inner_wrapper
    return outer_wrapper


def read_farmi_file(filename):
    with open(filename, 'rb') as f:
        unpacker = msgpack.Unpacker(f)
        for value in unpacker:
            yield value
