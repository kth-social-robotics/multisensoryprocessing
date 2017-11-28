# python3 watson_asr.py

import json
import pika
import zmq
from threading import Thread
from watson_developer_cloud import AuthorizationV1
from watson_developer_cloud import SpeechToTextV1
import websocket
import msgpack
import time
from twisted.python import log
from twisted.internet import reactor
import sys
sys.path.append('../..')
from shared import MessageQueue
import urllib.parse
from pprint import pprint
import yaml
from shared import create_zmq_server, MessageQueue

DEBUG = False

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Define server
zmq_socket, zmq_server_addr = create_zmq_server()
mq = MessageQueue('asr-preprocessor')

mq.publish(
    exchange='pre-processor',
    routing_key=settings['messaging']['asr_processing'],
    body={'address': zmq_server_addr, 'file_type': 'txt'}
)

with open('watson_credentials.json') as f:
    credentials = json.loads(f.read())
if not credentials:
    exit('no credentials')

api_base_url = credentials['url']
authorization = AuthorizationV1(username=credentials['username'], password=credentials['password'])
token = authorization.get_token(url=api_base_url)

def create_regognition_method_str(api_base_url):
	parsed_url = urllib.parse.urlparse(api_base_url)
	return urllib.parse.urlunparse(("wss", parsed_url.netloc, parsed_url.path + "/v1/recognize", parsed_url.params, parsed_url.query, parsed_url.fragment, ))

recognition_method_url = create_regognition_method_str(api_base_url)

class WatsonASR(object):
    START_MESSAGE = {
      'action': 'start',
      'content-type': 'audio/l16;rate=44100',
      'word_confidence': True,
      'timestamps': True,
      'interim_results' : True,
      'inactivity_timeout': -1
    }

    def __init__(self, zmq_address, api_base_url, token, on_message_callback):
        self.zmq_address = zmq_address
        self.api_base_url = api_base_url
        self.token = token
        self.on_message_callback = on_message_callback

        self._running = True
        self.timer = None
        self.last_timer = None

        thread = Thread(target = self.connect_to_watson)
        thread.deamon = True
        thread.start()

    def run(self, ws):
        context = zmq.Context()
        s = context.socket(zmq.SUB)
        s.setsockopt_string(zmq.SUBSCRIBE, u'')
        s.connect(self.zmq_address)

        if DEBUG: print(json.dumps(self.START_MESSAGE))
        ws.send(json.dumps(self.START_MESSAGE).encode('utf-8'))

        while True:
            data = s.recv()
            if data == b'CLOSE':
                print("got CLOSE msg. stopping..")
                self._running = False
                break
            msgdata, timestamp = msgpack.unpackb(data, use_list=False)
            if not self.timer: self.timer = timestamp
            self.last_timer = timestamp
            try:
                ws.send(msgdata, websocket.ABNF.OPCODE_BINARY)
            except websocket._exceptions.WebSocketConnectionClosedException:
                print("couldn't send, restarting...")
                break
        s.close()
        ws.close()
        print("thread terminating...")

    def on_open(self, ws):
        thread = Thread(target = self.run, args=(ws, ))
        thread.deamon = True
        thread.start()

    def on_error(self, ws, error):
        """Print any errors."""
        print('ERROR', error)

    def on_close(self, ws):
        print("Closed down websocket")

    def connect_to_watson(self):
        headers = {'X-Watson-Authorization-Token': self.token}

        while self._running:
            try:
                if DEBUG: print('connecting to watson...')
                ws = websocket.WebSocketApp(
                    self.api_base_url,
                    header=headers,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_open=self.on_open
                )
                ws.run_forever()
            except:
                'restarting'
        print('DONE')

    def on_message(self, ws, m):
        msg = json.loads(str(m))
        if msg.get('error'):
            print('>> {}'.format(msg))

        if msg.get('results'):
            data = {
                'time_start_asr': self.timer,
                'time_until_asr': self.last_timer,
                'text': msg['results'][0].get('alternatives', [{}])[0].get('transcript'),
                'final': msg["results"][0]["final"],
                'confidence': msg['results'][0].get('alternatives', [{}])[0].get('confidence')
            }
            if msg["results"][0]["final"]:
                self.timer = None
            self.on_message_callback(data)

def callback(_mq, get_shifted_time, routing_key, body):
    #participant = routing_key.rsplit('.', 1)[1]
    participant = 1
    print('connected {}'.format(routing_key))

    def on_message(data):
        if data["final"]:
            if DEBUG: print(data)
            # _mq.publish(
            #     exchange='pre-processor',
            #     routing_key='asr.data.{}'.format(participant),
            #     body=data
            # )
            zmq_socket.send(msgpack.packb((data, mq.get_shifted_time())))

    WatsonASR(body.get('address'), recognition_method_url, token, on_message)

mq = MessageQueue('asr-preprocessor')
mq.bind_queue(exchange='sensors', routing_key='microphone.new_sensor.*', callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()

zmq_socket.send(b'CLOSE')
zmq_socket.close()
