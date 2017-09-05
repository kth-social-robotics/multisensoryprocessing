import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind('tcp://*:45321')
while True:
    message = socket.recv()
    socket.send_string(str(time.time()))
