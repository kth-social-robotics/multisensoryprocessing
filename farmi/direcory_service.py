import time
from datetime import datetime

import zmq

PUBLISHER_PORT = 5561
SYNCSERVICE_PORT = 5562
SYNCSERVICE2_PORT = 5563
HEARTBEAT_PORT = 5564
SERVICES_PORT = 5565


def start_directory_service():
    context = zmq.Context()
    available_topics = {}

    publisher = context.socket(zmq.PUB)
    publisher.bind(f'tcp://*:{PUBLISHER_PORT}')

    syncservice = context.socket(zmq.REP)
    syncservice.bind(f'tcp://*:{SYNCSERVICE_PORT}')

    syncservice2 = context.socket(zmq.REP)
    syncservice2.bind(f'tcp://*:{SYNCSERVICE2_PORT}')

    poller = zmq.Poller()
    poller.register(syncservice, zmq.POLLIN)
    poller.register(syncservice2, zmq.POLLIN)

    while True:
        socks = dict(poller.poll())
        if syncservice in socks:
            topic = syncservice.recv_json()
            syncservice.send_string(str(time.time()))
            available_topics[topic['name']] = topic['address']
            publisher.send_json(available_topics)
        if syncservice2 in socks:
            syncservice2.recv()
            syncservice2.send_string(str(time.time()))
            publisher.send_json(available_topics)


if __name__ == '__main__':
    start_directory_service()