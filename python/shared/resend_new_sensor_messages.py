import zmq
import time
from threading import Thread


def resend_new_sensor_messages():
    def run():
        time.sleep(2)
        context = zmq.Context()
        s = context.socket(zmq.REQ)
        s.connect('tcp://localhost:45322')
        s.send_string('new_sensor')
        s.recv()

    thread2 = Thread(target = run)
    thread2.deamon = True
    thread2.start()
