"""
Copyright (c) 2017 Eyeware Tech SA, http://www.eyeware.tech

Communication interface with the GazeSense interface.

Requirements:
- Zeromq: http://zeromq.org/bindings:python
"""
from threading import Thread
import zmq
import time


class ZmqClient(object):
    context = zmq.Context()

    def __init__(self, host, port):
        self.socket = self.context.socket(zmq.SUB)
        connection = "tcp://%s:%d" % (host, port)
        self.socket.connect(connection)
        self.socket.setsockopt(zmq.SUBSCRIBE, "")

    def __del__(self):
        self.close()

    def recv(self):
        try:
            json_msg = self.socket.recv_json(flags=zmq.NOBLOCK)
            return json_msg
        except:
            return None

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None

class GazeSenseSub:
    def __init__(self, callback=None, verbose=True, port=8001):
        self.host, self.port = 'localhost', port
        self.running_ = True
        self.connected_ = False  # Indicates that it is not receiving data
        self.tracking_ = False  # Indicates whether it is receiving tracking data
        self.verbose_ = verbose
        self.thread = Thread(target=self.receiver_loop)
        self.thread.start()
        self.current_gaze = 'NA'
        self.callback_ = callback

    def __del__(self):
        self.running_ = False

    def is_tracking(self):
        return self.tracking_

    def is_connected(self):
        return self.connected_

    def get_current_gaze(self):
        return self.current_gaze

    def stop(self):
        print("Disconnected...")  # added by Eran
        self.running_ = False

    def receiver_loop(self):
        client = ZmqClient(self.host, self.port)
        time_of_last_message = -10000000
        time_of_last_data = -10000000
        if self.verbose_:
            print('Waiting for connection...')
        while self.running_:
            novelty = False
            data = client.recv()
            if data is None:
                time.sleep(0.1)
            else:
                if 'GazeCoding' in data.keys():
                    self.current_gaze = data['GazeCoding']
                    novelty = True
                    time_of_last_data = time.time()
                time_of_last_message = time.time()
            is_tracking = time.time() - time_of_last_data < 0.5
            is_connected = time.time() - time_of_last_message < 2.0

            novelty = novelty or (is_connected != self.connected_)
            novelty = novelty or (is_tracking != self.tracking_)

            if self.verbose_ and (self.tracking_ != is_tracking):
                print('Tracking updated: Tracking? {}'.format(is_tracking))
            if self.verbose_ and not is_connected and self.connected_:
                print('Waiting for connection...')
            if self.verbose_ and is_connected and not self.connected_:
                print('Connected...')

            self.connected_ = is_connected
            self.tracking_ = is_tracking
            if not self.tracking_:
                self.current_gaze = 'NA'
            if novelty and self.callback_:
                data = {}
                data['GazeCoding'] = self.current_gaze
                data['InTracking'] = self.tracking_
                data['ConnectionOK'] = self.connected_
                self.callback_(data)
        client.close()
