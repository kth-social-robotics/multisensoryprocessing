import time
from threading import Thread

import zmq

from farmi.farmi import Farmi
from farmi.farmi_file import FarmiFile
from farmi.serialization import serialize
from farmi.utils import get_ip


class Publisher(Farmi):
    def __init__(
        self,
        topic,
        local_save=None,
        directory_service_address="tcp://127.0.0.1:5555",
        heartbeat_frequency=5,
        compress_data=None,
    ):
        super().__init__(directory_service_address)
        self.topic = topic
        self.heartbeat_frequency = heartbeat_frequency
        self.pub_address = None
        self.pub_socket = self.context.socket(zmq.PUB)
        self.local_save = local_save
        self.compress_data = compress_data
        self._create_publisher()
        Thread(target=self._heartbeat).start()

        self.file_handle = self._create_farmi_file()

    def _create_farmi_file(self):
        if self.local_save:
            dir_name = self.local_save if isinstance(self.local_save, str) else "."
            return FarmiFile(f"{dir_name}/{self.topic}-{{}}.farmi")
        else:
            return None

    def _heartbeat(self):
        while not self.exit.is_set():
            self.directory_service.send_json(
                {"action": "HEARTBEAT", "topic": self.topic, "time": time.time()}
            )
            response = self.directory_service.recv_string()
            if response == "NOT_REGISTERED":
                self._register()
            if self.compress_data and self.file_handle:
                self.file_handle.check_file_size()
            self.exit.wait(self.heartbeat_frequency)

    def _register(self):
        self.directory_service.send_json(
            {"action": "REGISTER", "topic": self.topic, "address": self.pub_address}
        )
        self.directory_service.recv_string()

    def _create_publisher(self):
        zmq_port = self.pub_socket.bind_to_random_port("tcp://*", max_tries=150)
        self.pub_address = "tcp://{}:{}".format(get_ip(), zmq_port)
        self._register()

    def end_recording(self):
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = self._create_farmi_file()

    def send(self, data, timestamp=None):
        if not timestamp:
            timestamp = time.time()
        data_time = timestamp + self.time_offset

        serialized_data = serialize([self.topic, data_time, data])

        if self.file_handle:
            self.file_handle.write(data=serialized_data, timestamp=data_time)

        self.pub_socket.send_multipart(
            (
                self.topic.encode("utf-8"),
                str(data_time).encode("utf-8"),
                serialized_data,
            )
        )

    def close(self):
        self.directory_service.send_json({"action": "DEREGISTER", "topic": self.topic})
        self.directory_service.recv()
        super().close()
        self.pub_socket.send(b"CLOSE")
        self.pub_socket.close()
        if self.file_handle:
            self.file_handle.close()
