
import zmq
import pika
import time
import msgpack
import cv2
import sys
import zmq
import subprocess as sp
import numpy as np
sys.path.append('../..')
from shared import create_zmq_server, MessageQueue


zmq_socket, zmq_server_addr = create_zmq_server()


if len(sys.argv) != 2:
    exit('error. python video.py [color]')
participant = sys.argv[1]

mq = MessageQueue('video-scren_capture-sensor')
mq.publish(
    exchange='sensors',
    routing_key='video.new_sensor.{}'.format(participant),
    body={
        'address': zmq_server_addr,
        'file_type': 'ffmpeg-video',
        'img_size': {
            'width': 1280,
            'height': 720,
            'channels': 3,
            'fps': 30,
        }
    }
)

command = [
    'ffmpeg', '-y',
    '-f', 'avfoundation',
    '-framerate', '30',
    '-i', '0',
    '-f', 'image2pipe',
    '-pix_fmt', 'bgr24',
    '-vcodec', 'rawvideo', '-'
]
pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)

while True:
    raw_image = pipe.stdout.read(1280*720*3)
    pipe.stdout.flush()
    zmq_socket.send(msgpack.packb((raw_image, time.time())))

input('[*] Serving at {}. To exit press enter'.format(zmq_server_addr))

sock.close()
zmq_socket.close()
