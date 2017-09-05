import tempfile
import sys
import zmq
import msgpack
sys.path.append('..')
from smb.SMBConnection import SMBConnection
from shared import MessageQueue
import datetime
import yaml
import os
from threading import Thread
import queue
import json
import time


with open('.smb_credentials.json') as f:
    credentials = json.loads(f.read())
if not credentials:
    exit('no credentials')

SETTINGS_FILE = os.path.abspath(
    os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, 'settings.yaml')
)
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

session_name = datetime.datetime.now().isoformat().replace('.', '_').replace(':', '_')

q = queue.Queue()
running = True


def callback(mq, get_shifted_time, routing_key, body):
    def run():
        global running

        conn = SMBConnection(
            credentials['username'],
            credentials['password'],
            credentials['client_machine_name'],
            credentials['server_name'],
            use_ntlm_v2 = True
        )
        assert conn.connect(settings['file_storage']['host'], settings['file_storage']['port'])


        try:
            conn.createDirectory(settings['file_storage']['service_name'], '/logger/{}'.format(session_name))
        except:
            pass

        a = 0
        go_on = True
        while go_on:
            try:
                conn.createDirectory(settings['file_storage']['service_name'], '/logger/{}/{}-{}'.format(session_name, routing_key, a))
                go_on = False
            except:
                a += 1

        conn.close()
        log_file = '/logger/{}/{}-{}/data.{}'.format(session_name, routing_key, a, body.get('file_type', 'unknown'))
        print('[{}] streamer connected'.format(log_file))

        file_obj = tempfile.NamedTemporaryFile()
        file_obj.seek(0)



        context = zmq.Context()
        s = context.socket(zmq.SUB)
        s.setsockopt_string( zmq.SUBSCRIBE, '' )
        s.RCVTIMEO = 10000
        s.connect(body['address'])

        t = time.time()

        while running:
            try:
                data = s.recv()
                msgdata, timestamp = msgpack.unpackb(data, use_list=False)
                file_obj.write(msgdata)

                if time.time() - t >= 2:
                    print('write', time.time() - t)
                    t = time.time()
                    file_obj.seek(0)
                    q.put((log_file, file_obj))
            except zmq.error.Again:
                break

        file_obj.seek(0)
        q.put((log_file, file_obj))
        s.close()
        print('[{}] streamer closed'.format(log_file))

    _thread = Thread(target = run)
    _thread.deamon = True
    _thread.start()


def storage_writer():
    global running

    while running or q.qsize() != 0:
        log_file, data = q.get()
        trying = 5
        while trying > 0:
            try:
                conn = SMBConnection(
                    credentials['username'],
                    credentials['password'],
                    credentials['client_machine_name'],
                    credentials['server_name'],
                    use_ntlm_v2 = True
                )
                assert conn.connect(settings['file_storage']['host'], settings['file_storage']['port'])
                second_file_obj = tempfile.NamedTemporaryFile()
                second_file_obj.seek(0)
                second_file_obj.write(data.read())
                second_file_obj.seek(0)
                print('writing.....')
                conn.storeFile(settings['file_storage']['service_name'], log_file, second_file_obj)
                print('done writing.....')
                trying = 0
                break
            except:
                print('failed')
                time.sleep(trying/2)
                trying -= 1
        print('{} writes left to do..', q.qsize())
    conn.close()
    data.close()
    print('writer closed'.format(log_file))

thread = Thread(target = storage_writer)
thread.deamon = True
thread.start()


mq = MessageQueue('logger')
mq.bind_queue(
    exchange='sensors', routing_key='*.new_sensor.*', callback=callback
)


thread2 = Thread(target = mq.listen)
thread2.deamon = True
thread2.start()

input('[*] Waiting for messages. To exit press enter')
running = False
print('ugly hack: now press CTRL-C')
mq.stop()
