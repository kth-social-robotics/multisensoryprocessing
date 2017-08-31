import time
import sys
import yaml
import os
import pika
import zmq
import json


SETTINGS_FILE = os.path.abspath(
    os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, 'settings.yaml')
)


class MessageQueue(object):
    def __init__(self, name):
        self.name = name
        self.settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

        messaging_settings = self.settings['messaging']
        broker_host = messaging_settings['broker_host']
        broker_port = messaging_settings['broker_port']
        broker_user = messaging_settings['broker_user']
        broker_pass = messaging_settings['broker_pass']

        credentials = pika.PlainCredentials(broker_user, broker_pass)
        connection_parameters = pika.ConnectionParameters(
            host=broker_host, port=broker_port, credentials=credentials
        )
        self.connection = pika.BlockingConnection(connection_parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.settings['messaging']['pre_processing'], exchange_type='topic')
        self.channel.exchange_declare(exchange=self.settings['messaging']['sensors'], exchange_type='topic')
        self.channel.exchange_declare(exchange=self.settings['messaging']['wizard'], exchange_type='topic')
        self.channel.exchange_declare(exchange=self.settings['messaging']['environment'], exchange_type='topic')
        self.channel.exchange_declare(exchange=self.settings['messaging']['fatima'], exchange_type='topic')

        self.set_time_offset()

    def set_time_offset(self):
        time_server_host = self.settings['messaging']['time_server_host']
        context = zmq.Context()
        s = context.socket(zmq.REQ)
        print('connecting to time server..', time_server_host)
        s.connect(time_server_host)
        s.send(b'')
        message = s.recv()
        self.time_offset = float(message) - time.time()
        print('got time from time server!')

    def timestamp(self, msg, timestamp_type):
        timestamps = msg.get('timestamps', [])
        if timestamps:
            if timestamps[-1].get('name') != self.name:
                timestamps.append({'name': self.name})
            timestamps[-1][timestamp_type] = self.get_shifted_time()
        else:
            timestamps.append({'name': self.name, timestamp_type: self.get_shifted_time()})

        msg['timestamps'] = timestamps
        return msg

    def publish(self, exchange='', routing_key='', body={}, no_time=False):
        if not no_time:
            self.timestamp(body, 'departed')

        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=json.dumps(body))

    def get_shifted_time(self):
        return time.time() + self.time_offset

    def bind_queue(self, exchange='', routing_key='', callback=None, no_time=False, queue_name=None, callback_wrapper_func=None):
        result = self.channel.queue_declare(exclusive=True)
        if not queue_name:
            queue_name = result.method.queue
        self.channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=routing_key)
        #self.channel.basic_qos(prefetch_count=50)

        if not callback_wrapper_func:
            def callback_wrapper(ch, method, properties, body):
                if type(body) == bytes:
                    body = body.decode("utf-8")
                msg = json.loads(body)
                if not no_time:
                    self.timestamp(msg, 'arrived')
                callback(self, self.get_shifted_time, method.routing_key, msg)
            callback_wrapper_func = callback_wrapper

        self.channel.basic_consume(callback_wrapper_func, queue=queue_name)

    def disconnect(self, routing_key):
        self.publish(exchange=self.settings['messaging']['sensors'], routing_key=routing_key, body={})

    def stop(self):
        self.channel.stop_consuming()
        self.connection.close()

    def listen(self):
        self.channel.start_consuming()
