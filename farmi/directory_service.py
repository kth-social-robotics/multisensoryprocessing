import json
import logging
import time

import zmq

from farmi.utils import get_ip

logger = logging.getLogger(__name__)


class DirectoryService(object):
    def __init__(self, port=5555, purge_timeout=20):
        self._topics = {}
        self.purge_timeout = purge_timeout
        context = zmq.Context()
        self.rep_socket = context.socket(zmq.REP)
        self.rep_socket.bind("tcp://*:{}".format(port))

        self.publisher = context.socket(zmq.PUB)
        pub_port = self.publisher.bind_to_random_port("tcp://*", max_tries=150)
        self.pub_address = "tcp://{}:{}".format(get_ip(), pub_port)

    @property
    def topics(self):
        self._purge_topics()
        return self._topics

    def _purge_topics(self):
        to_be_deleted = []
        for topic, info in self._topics.items():
            if time.time() - info["latest_heartbeat"] > self.purge_timeout:
                to_be_deleted.append(topic)

        for topic in to_be_deleted:
            self._deregister(topic)

    def _deregister(self, topic):
        if self._topics.get(topic):
            self._topics.pop(topic)
            self._broadcast(json.dumps({"action": "DEREGISTERED", "topic": topic}))

    def listen(self):
        while True:
            raw_msg = self.rep_socket.recv_string()
            try:
                msg = json.loads(raw_msg)
            except ValueError:
                logger.info("MALFORMED_JSON" + raw_msg)
                self.rep_socket.send_string("MALFORMED_JSON")
                continue

            action = msg.get("action")

            if action == "GET_PUB_ADDRESS":
                response = self.handle_get_pub_address(msg)
            elif action == "REGISTER":
                response = self.handle_register(msg)
            elif action == "DEREGISTER":
                response = self.handle_deregister(msg)
            elif action == "SYNC":
                response = self.handle_sync(msg)
            elif action == "ANNOUNCE":
                response = self.handle_announce(msg)
            elif action == "HEARTBEAT":
                response = self.handle_heartbeat(msg)
            elif action == "TOPICS":
                response = self.handle_topics(msg)
            else:
                response = "COMMAND_NOT_FOUND"

            logger.info("received msg: {}, responded: {}".format(msg, response))
            self.rep_socket.send_string(response)

    def _broadcast(self, data, topic=""):
        logger.info("broadcasting: {}".format(data))
        self.publisher.send_multipart([topic.encode("utf-8"), data.encode("utf-8")])

    def _check_required_args(self, msg, required):
        return all([msg.get(x) for x in required])

    def handle_topics(self, msg):
        return json.dumps(self.topics)

    def handle_get_pub_address(self, msg):
        return self.pub_address

    def handle_deregister(self, msg):
        if not self._check_required_args(msg, ["topic"]):
            return "MISSING_INFORMATION"
        self._deregister(msg.get("topic"))
        return "OK"

    def handle_register(self, msg):
        if not self._check_required_args(msg, ["topic", "address"]):
            return "MISSING_INFORMATION"

        topic, address = msg.get("topic"), msg.get("address")

        if self.topics.get(topic):
            self._deregister(topic)
            # return 'TOPIC_ALREADY_REGISTERED'

        self.topics[topic] = {"address": address, "latest_heartbeat": time.time()}
        self._broadcast(
            json.dumps({"action": "REGISTERED", "topic": topic, "address": address})
        )
        return "OK"

    def handle_sync(self, msg):
        return str(time.time())

    def handle_announce(self, msg):
        if not self._check_required_args(msg, ["msg"]):
            return "MISSING_INFORMATION"

        self._broadcast(msg.get("msg"))
        return "OK"

    def handle_heartbeat(self, msg):
        if not self._check_required_args(msg, ["topic", "time"]):
            return "MISSING_INFORMATION"

        logger.info("got HEARTBEAT: {}".format(msg))

        topic, time_ = msg.get("topic"), msg.get("time")

        if self._topics.get(topic):
            self._topics[topic]["latest_heartbeat"] = time.time()

            self._broadcast(
                json.dumps(
                    {
                        "action": "HEARTBEAT",
                        "topic": topic,
                        "time": time.time(),
                        "sender_time": time_,
                    }
                )
            )
            return "OK"
        else:
            return "NOT_REGISTERED"
