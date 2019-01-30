import time
from threading import Thread
import msgpack
import msgpack_numpy as m
m.patch()
import zmq
from farmi.utils import get_ip
from farmi.farmi import Farmi


class Publisher(Farmi):
    def __init__(self, topic, local_save=None, directory_service_address='tcp://127.0.0.1:5555', heartbeat_frequency=20):
        super().__init__(directory_service_address)
        self.topic = topic
        self.heartbeat_frequency = heartbeat_frequency

        self.pub_socket = self.context.socket(zmq.PUB)
        
        self._create_publisher()
        Thread(target=self._heartbeat).start()
        
        if local_save:
            self.packer = msgpack.Packer()
            dir_name = local_save if isinstance(local_save, str) else '.'
            timestamp = time.strftime("%Y_%m_%d_%H_%M_%S")
            self.file_handle = open('{}/{}-{}.farmi'.format(dir_name, timestamp, self.topic), 'wb')
        else:
            self.file_handle = None

    def _heartbeat(self):
        while not self.exit.is_set():
            self.directory_service.send_json({
                'action': 'HEARTBEAT',
                'topic': self.topic,
                'time': time.time()
            })
            self.directory_service.recv()
            self.exit.wait(self.heartbeat_frequency)


    def _create_publisher(self):
        zmq_port = self.pub_socket.bind_to_random_port('tcp://*', max_tries=150)
        zmq_server_addr = 'tcp://{}:{}'.format(get_ip(), zmq_port)
        self.directory_service.send_json({
            'action': 'REGISTER',
            'topic': self.topic,
            'address': zmq_server_addr
        })
        response = self.directory_service.recv_string()
        if response == 'TOPIC_ALREADY_REGISTERED':
            raise Exception('TOPIC_ALREADY_REGISTERED')


    def get_shifted_time(self):
        return time.time() + self.time_offset

    def send(self, data, timestamp=None):
        if not timestamp:
            timestamp = time.time()
        data_time = timestamp + self.time_offset
        if self.file_handle:
            self.file_handle.write(self.packer.pack((self.topic, data_time, data)))
            self.file_handle.flush()
        self.pub_socket.send_multipart([self.topic.encode('utf-8'), str(data_time).encode('utf-8'), msgpack.packb(data, use_bin_type=True)])

    def close(self):
        super().close()

        self.pub_socket.send(b'CLOSE')
        self.pub_socket.close()
        if self.file_handle:
            self.file_handle.close()
