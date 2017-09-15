import pyaudio
import sys
import time
import msgpack
sys.path.append('../..')
import numpy as np
import re
from shared import create_zmq_server, MessageQueue
import sys
import datetime
from threading import Thread, Event


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 2000

zmq_socket, zmq_server_addr = create_zmq_server()


mq = MessageQueue('microphone-sensor')
p = pyaudio.PyAudio()


class MyThread(Thread):
    def __init__(self, mq, zmq_server_addr):
        Thread.__init__(self)
        self.stopped = Event()
        self.mq = mq
        self.zmq_server_addr = zmq_server_addr

    def run(self):
        while not self.stopped.wait(5):
            mq.publish(
                exchange='sensors',
                routing_key='microphone.new_sensor.A',
                body={'address': self.zmq_server_addr, 'file_type': 'audio'}
            )

thread = MyThread(mq, zmq_server_addr)
thread.daemon = True
thread.start()



def callback(in_data, frame_count, time_info, status):
    the_time = mq.get_shifted_time()
    zmq_socket.send(msgpack.packb((in_data, the_time)))
    return None, pyaudio.paContinue


stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
    stream_callback=callback
)
try:
    input('[*] Serving at {}. To exit press enter'.format(zmq_server_addr))
finally:
    stream.stop_stream()
    stream.close()
    zmq_socket.send(b'CLOSE')
    zmq_socket.close()
