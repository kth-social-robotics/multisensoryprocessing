from threading import Event
import zmq
import time


class Farmi(object):
    """docstring for Farmi"""
    def __init__(self, topic, directory_service_address='127.0.0.1:5555'):
        self.topic = topic
        self.exit = Event()
        self.context = zmq.Context()
        self._connect_to_directory_service(directory_service_address)
    
    def _connect_to_directory_service(self, directory_service_address):
        self.directory_service = self.context.socket(zmq.REQ)
        self.directory_service.connect('tcp://{}'.format(directory_service_address))
        self._sync_time()

    def _sync_time(self):
        self.time_offset = 0
        number_of_syncs = 3

        for i in range(number_of_syncs):
            self.directory_service.send_json({'action': 'SYNC'})
            time_offset = float(self.directory_service.recv_string()) - time.time()
            self.time_offset =+ time_offset

        self.time_offset /= number_of_syncs

    def close(self):
        self.exit.set()
        time.sleep(0.3)
        self.directory_service.send_json({
            'action': 'DEREGISTER',
            'topic': self.topic
        })
        self.directory_service.recv()
        self.directory_service.close()