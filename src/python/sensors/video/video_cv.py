import zmq
import pika
import time
import msgpack
import cv2
import sys
import zmq
import numpy as np
import subprocess
import scipy.ndimage
import datetime
sys.path.append('../..')
from shared import create_zmq_server, MessageQueue
zmq_socket, zmq_server_addr = create_zmq_server()


if len(sys.argv) != 3:
    exit('error. python video_cv.py [color] [camera]')
participant = sys.argv[1]
camera_id = int(sys.argv[2])





# process = subprocess.Popen(
#     ["/enterface/ffmpeg-20170711-0780ad9-win64-static/bin/ffmpeg.exe", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
#     stderr=subprocess.PIPE
# )
# process = subprocess.Popen(["lsusb"], stdout=subprocess.PIPE
# )
# out, err = process.communicate()
# print(out)
#
# data = str(err)
# stuff = [
#     ("white", data.index("vid_046d&pid_0843&mi_00#7&371f838&0&0000")),  # white webcam
#     ("blue", data.index("vid_046d&pid_0843&mi_00#6&c7f0d35&0&0000")),  # blue webcam
#     ("brown", data.index("046d&pid_08c9&mi_00#7&2ea013c4&0&0000"))  # brown webcam
# ]
#
# # sort by appearance
# sorted_devices = sorted(stuff, key=lambda x: x[1])

#device_id = [x[0] for x in sorted_devices].index(participant)

# for i in range(0, 4):
#     print('device id:', i)
#     camera = cv2.VideoCapture(i)
#     while True:
#         try:
#             _, frame = camera.read()
#             cv2.imshow('frame', frame)
#             cv2.waitKey(1)
#         except:
#             break
#     camera.release()
#     cv2.destroyAllWindows()
#
#
#
fourcc = cv2.VideoWriter_fourcc(*'MP4V')

camera = cv2.VideoCapture(camera_id)
width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT) # float

session_name = datetime.datetime.now().isoformat().replace('.', '_').replace(':', '_')
out = cv2.VideoWriter('{}.mp4'.format(session_name), fourcc, 30.0, (int(width), int(height)))



mq = MessageQueue('video-webcam-sensor')
mq.publish(
    exchange='sensors',
    routing_key='video.new_sensor.{}'.format(participant),
    body={
        'address': zmq_server_addr,
        'file_type': 'cv-video',
        'img_size': {
            'width': width / 2,
            'height': height / 2,
            'channels': 3,
            'fps': 30,
        }
    }
)
print('[*] Serving at {}. To exit press enter'.format(zmq_server_addr))
try:
    while True:
        _, frame = camera.read()
        out.write(frame)
        zmq_socket.send(msgpack.packb((scipy.ndimage.zoom(frame, (0.5, 0.5, 1), order=0).flatten().tobytes(), time.time())))

except KeyboardInterrupt:
    mq.disconnect('video.disconnected_sensor.{}'.format(participant))
    zmq_socket.send(b'CLOSE')
    zmq_socket.close()
