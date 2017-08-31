import tempfile
import sys
import zmq
import msgpack
sys.path.append('..')
from shared import MessageQueue, resend_new_sensor_messages
import datetime
import yaml
import os
from threading import Thread
import queue
import json
import time
import shutil

if len(sys.argv) != 2:
    print('No routing key given, assuming *.new_sensor.*')
    listen_to_routing_key = '*.new_sensor.*'
else:
    listen_to_routing_key = sys.argv[1]



SETTINGS_FILE = os.path.abspath(
    os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, 'settings.yaml')
)
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

session_name = datetime.datetime.now().isoformat().replace('.', '_').replace(':', '_')

log_path = os.path.join(settings['logging']['sensor_path'], session_name)



os.mkdir(log_path)
shutil.copy(os.path.join('..', 'settings.yaml'), os.path.join(log_path, 'settings.yaml'))
global_runner = True
running = {}
sockets = []

def callback(mq, get_shifted_time, routing_key, body):
    global running

    a = 0
    go_on = True
    q = queue.Queue()

    while go_on:
        try:
            os.mkdir(os.path.join(log_path, '{}-{}'.format(routing_key, a)))
            go_on = False
        except FileExistsError:
            a += 1




    log_file = os.path.join(
        log_path,
        '{}-{}'.format(routing_key, a), 'data.{}'.format(body.get('file_type', 'unknown'))
    )
    running[log_file] = True

    print('[{}] streamer connected'.format(log_file))
    with open(os.path.join(log_path, '{}-{}'.format(routing_key, a), 'info.txt'), 'w') as f:
        f.write(json.dumps(body))

    def run(log_file):
        global global_runner, running

        context = zmq.Context()
        s = context.socket(zmq.SUB)
        s.setsockopt_string( zmq.SUBSCRIBE, '' )
        # s.RCVTIMEO = 30000
        s.connect(body['address'])
        sockets.append(s)
        t = time.time()

        d = bytes()
        while running[log_file] and global_runner:
            data = s.recv()
            if data == b'CLOSE':
                print('close received')
                running[log_file] = False
                break
            d += data
            if time.time() - t > 5:
                q.put(d)
                d = bytes()

        global_runner = True
        if d:
            q.put(d)

        s.close()
        print('[{}] streamer closed'.format(log_file))


    def storage_writer(log_file):
        global global_runner, running
        with open(log_file, 'ab') as f:
            while global_runner or q.qsize() != 0:
                data = q.get()
                f.write(data)
                print('{} writes left to do..', q.qsize())
        print('writer closed'.format(log_file))

    _thread = Thread(target = run, args=(log_file, ))
    _thread.deamon = True
    _thread.start()


    thread = Thread(target = storage_writer, args=(log_file, ))
    thread.deamon = True
    thread.start()


mq = MessageQueue('logger')
mq.bind_queue(
    exchange='sensors', routing_key=listen_to_routing_key, callback=callback
)

resend_new_sensor_messages.resend_new_sensor_messages()
print('[*] Waiting for messages. To exit press CTRL-C')
try:
    mq.listen()
finally:
    global_runner = False
    for sock in sockets:
        print(sock.closed)
        if not sock.closed:
            sock.close()
    mq.stop()
