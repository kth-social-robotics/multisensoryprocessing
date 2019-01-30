from farmi.farmi import Farmi
import json
from collections import defaultdict
import zmq
import re


class Subscriber(Farmi):
    def __init__(self, directory_service_address='tcp://127.0.0.1:5555'):
        super().__init__(directory_service_address)
        self.topics = defaultdict(dict)
        self.poller = zmq.Poller()

        self.directory_service.send_json({'action': 'GET_PUB_ADDRESS'})
        sub_address = self.directory_service.recv_string()

        self.directory_service_sub = self.context.socket(zmq.SUB)
        self.directory_service_sub.connect(sub_address)
        self.directory_service_sub.subscribe('')

        self.poller.register(self.directory_service_sub, zmq.POLLIN)

    def get_matching_topics(self, topic):
        for topic_matchers in self.topics.keys():
            if topic_matchers.match(topic):
                yield topic_matchers

    def subscribe_to(self, topic, fn):
        if not isinstance(topic, re._pattern_type):
            topic = re.compile('%s$' % re.escape(topic))
        self.topics[topic]['fn'] = fn

        self.directory_service.send_json({'action': 'TOPICS'})
        topics = self.directory_service.recv_json()
        for received_topic, info in topics.items():
            for matching_topic in self.get_matching_topics(received_topic):
                self._add_topic(matching_topic, info['address'])

    def _add_topic(self, topic, address):
        self.topics[topic]['address'] = address
        socket = self.context.socket(zmq.SUB)
        socket.connect(address)
        socket.subscribe('')
        self.topics[topic]['socket'] = socket
        self.poller.register(self.topics[topic]['socket'], zmq.POLLIN)

    def _remove_topic(self, topic):
        if self.topics[topic].get('socket'):
            self.poller.unregister(self.topics[topic]['socket'])
            self.topics[topic]['socket'].close()
        
        if self.topics[topic]:
            self.topics.pop(topic)

    def listen(self):
        while not self.exit.is_set():
            poller = dict(self.poller.poll())
            for poll in poller:
                if poll == self.directory_service_sub:
                    _, raw_msg = poll.recv_multipart()
                    msg = json.loads(raw_msg.decode('utf-8'))
                    action = msg.get('action')
                    if action == 'REGISTERED':
                        topic, address = msg.get('topic'), msg.get('address')
                        for matching_topic in self.get_matching_topics(topic):
                            if self.topics[matching_topic].get('address') != address:
                                self._add_topic(matching_topic, address)
                            
                    elif action == 'DEREGISTERED':
                        self._remove_topic(msg.get('topic'))
                    for matching_topic in self.get_matching_topics(action):
                        self.topics[matching_topic]['fn'](msg)
                else:
                    for topic in self.topics.values():
                        if topic.get('socket') == poll:
                            msg = poll.recv_multipart()
                            topic['fn'](msg)
