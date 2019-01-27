from farmi.farmi import Farmi
import json
from collections import defaultdict
from threading import Thread
import zmq


class Subscriber(Farmi):
    def __init__(self, topic, fn, directory_service_address='127.0.0.1:5555'):
        super().__init__(topic, directory_service_address)
        self.fn = fn
        self.topic = topic
        self.topics = defaultdict(dict)
        self.poller = zmq.Poller()

        Thread(target=self._subscribe_to_directory_service).start()

    def _subscription_filter(self, topic):
        return self.topic == topic

    def _add_topic(self, topic, address):
        self.topics[topic]['address'] = address
        socket = self.context.socket(zmq.SUB)
        socket.connect(address)
        socket.subscribe('')
        self.topics[topic]['socket'] = socket
        self.poller.register(self.topics[topic]['socket'], zmq.POLLIN)

    def _remove_topic(self, topic):
        self.poller.unregister(self.topics[topic]['socket'])
        self.topics[topic]['socket'].close()
        self.topics.pop(topic)


    def _subscribe_to_directory_service(self):
        self.directory_service.send_json({'action': 'GET_PUB_ADDRESS'})
        sub_address = self.directory_service.recv_string()

        self.directory_service.send_json({'action': 'TOPICS'})
        topics = self.directory_service.recv_json()
        for topic, info in topics.items():
            if self._subscription_filter(topic):
                self._add_topic(topic, info['address'])

        directory_service_sub = self.context.socket(zmq.SUB)
        directory_service_sub.connect(sub_address)
        directory_service_sub.subscribe('')

        while not self.exit.is_set():
            _, raw_msg = directory_service_sub.recv_multipart()
            msg = json.loads(raw_msg.decode('utf-8'))
            action = msg.get('action')
            if action == 'REGISTERED':
                topic, address = msg.get('topic'), msg.get('address')
                if self._subscription_filter(topic) and self.topics[topic].get('address') != address:
                    self._add_topic(topic, address)
            elif action == 'DEREGISTERED':
                topic = msg.get('topic')


    def listen(self):
        while not self.exit.is_set():
            poller = dict(self.poller.poll())
            for poll in poller:
                msg = poll.recv_multipart()
                self.fn(msg)
