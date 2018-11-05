import socket
import time
from threading import Thread

import msgpack
import zmq

DIRECTORY_SERVICE_ANNOUNCE_PORT = 5562


class FarmiUnit(object):
    def __init__(self, topic, send_pyobj=False, local_save=None, directory_service_ip='127.0.0.1'):
        self.zmq_socket = None
        self.zmq_server_addr = None
        self.topic = topic
        self.send_pyobj = send_pyobj
        self.create_zmq_server()

        context = zmq.Context()
        self.directory_service = context.socket(zmq.REQ)
        self.directory_service.connect(f'tcp://{directory_service_ip}:{DIRECTORY_SERVICE_ANNOUNCE_PORT}')
        self.directory_service.send_json({'name': self.topic, 'address': self.zmq_server_addr})
        message = self.directory_service.recv_string()
        self.time_offset = float(message) - time.time()
        self.timestamp = time.strftime("%Y_%m_%d_%H_%M_%S")
        if local_save:
            self.packer = msgpack.Packer()
            dir_name = local_save if isinstance(local_save, str) else '.'
            self.file_handle = open(f'{dir_name}/{self.timestamp}-{self.topic}.farmi', 'wb')
        else:
            self.file_handle = None

    def heartbeat(self):
        def heartbeat_handler():
            context = zmq.Context()
            self.directory_service.connect(f'tcp://{directory_service_ip}:{DIRECTORY_SERVICE_ANNOUNCE_PORT}')

        Thread(target=heartbeat_handler).start()


    def create_zmq_server(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except OSError:
            print('falling back to using localhost..')
            ip = 'localhost'

        # Set up zmq server
        context = zmq.Context()
        self.zmq_socket = context.socket(zmq.PUB)
        zmq_port = self.zmq_socket.bind_to_random_port('tcp://*', max_tries=150)
        self.zmq_server_addr = 'tcp://{}:{}'.format(ip, zmq_port)
        print(self.zmq_server_addr)

    def get_shifted_time(self):
        return time.time() + self.time_offset

    def send(self, data, sub_topic='*'):
        if self.file_handle:
            self.file_handle.write(self.packer.pack((self.topic, sub_topic, self.get_shifted_time(), data)))
            self.file_handle.flush()
        if self.send_pyobj:
            self.zmq_socket.send_pyobj((sub_topic, self.get_shifted_time(), data))
        else:
            self.zmq_socket.send_multipart([self.topic.encode('utf-8'), sub_topic.encode('utf-8'), str(self.get_shifted_time()).encode('utf-8'), msgpack.packb(data, use_bin_type=True)])

    def close(self):
        # self.directory_service.send(b'CLOSE' + self.topic.encode('utf-8')) TODO: close directory service
        self.zmq_socket.send(b'CLOSE')
        self.zmq_socket.close()
        if self.file_handle:
            self.file_handle.close()