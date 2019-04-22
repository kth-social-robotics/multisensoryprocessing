import json
import re
from collections import defaultdict

import zmq

from farmi.farmi import Farmi
from farmi.serialization import deserialize


class Subscriber(Farmi):
    def __init__(self, directory_service_address="tcp://127.0.0.1:5555"):
        super().__init__(directory_service_address)
        self.topics = defaultdict(dict)
        self.poller = zmq.Poller()

        self.directory_service.send_json({"action": "GET_PUB_ADDRESS"})
        sub_address = self.directory_service.recv_string()

        self.directory_service_sub = self.context.socket(zmq.SUB)
        self.directory_service_sub.connect(sub_address)
        self.directory_service_sub.subscribe("")

        self.poller.register(self.directory_service_sub, zmq.POLLIN)

    def get_matching_topics(self, topic):
        for topic_matchers in self.topics.keys():
            if topic_matchers.match(topic):
                yield topic_matchers

    def subscribe_to(self, topic, fn):
        try:
            topic.match("")
        except:
            topic = re.compile("^%s$" % re.escape(topic))
        self.topics[topic]["fn"] = fn

        self.directory_service.send_json({"action": "TOPICS"})
        topics = self.directory_service.recv_json()
        for received_topic, info in topics.items():
            for matching_topic in self.get_matching_topics(received_topic):
                self._add_topic(matching_topic, info["address"])

    def _add_topic(self, topic, address):
        self.topics[topic]["address"] = address
        socket = self.context.socket(zmq.SUB)
        socket.connect(address)
        socket.subscribe("")
        self.topics[topic]["socket"] = socket
        self.poller.register(self.topics[topic]["socket"], zmq.POLLIN)

    def _remove_topic(self, topic):
        if self.topics[topic].get("socket"):
            self.poller.unregister(self.topics[topic]["socket"])
            self.topics[topic]["socket"].close()
            self.topics[topic].pop("socket")
            self.topics[topic].pop("address")

    def close(self):
        for topic, info in self.topics.items():
            if info["socket"]:
                info["socket"].close()
        super().close()

    def listen(self):
        while not self.exit.is_set():
            poller = dict(self.poller.poll())
            for poll in poller:
                raw_msg = poll.recv_multipart()
                if poll == self.directory_service_sub:
                    msg = json.loads(raw_msg[1].decode("utf-8"))
                    action = msg.get("action")
                    if action == "REGISTERED":
                        topic, address = msg.get("topic"), msg.get("address")
                        for matching_topic in self.get_matching_topics(topic):
                            if self.topics[matching_topic].get("address") != address:
                                self._add_topic(matching_topic, address)
                    elif action == "DEREGISTERED":
                        for matching_topic in list(
                            self.get_matching_topics(msg.get("topic"))
                        )[:]:
                            self._remove_topic(matching_topic)
                    for matching_topic in self.get_matching_topics(action):
                        self.topics[matching_topic]["fn"](
                            msg.get("topic"), msg.get("time"), msg
                        )
                else:
                    for topic in self.topics.values():
                        if topic.get("socket") == poll:
                            if len(raw_msg) == 3:
                                try:
                                    topic_, time_, body = raw_msg
                                except ValueError as e:
                                    print(raw_msg)
                                    raise e
                                deserialized_body = deserialize(body)
                                if isinstance(
                                    deserialized_body, list
                                ) and deserialized_body[0] == topic_.decode("utf-8"):
                                    b = deserialized_body[2]
                                else:
                                    b = deserialized_body
                                topic["fn"](
                                    topic_.decode("utf-8"),
                                    float(time_.decode("utf-8")),
                                    b,
                                )
