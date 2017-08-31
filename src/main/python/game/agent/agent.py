# import fatima
from furhat import connect_to_iristk
import pika
# from .. import Player
from threading import Thread
import json
import sys
sys.path.append('../..')
from shared import MessageQueue
# etc..


class Agent(object):
    """docstring for Agent."""

    FURHAT_IP = '192.168.0.111'
    FURHAT_AGENT_NAME = 'furhat6'
    RABBITMQ_CONNECTION = {'host': 'localhost', 'port': 32777}

    def __init__(self, environment):
        super(Agent, self).__init__()
        self.environment = environment

        # TODO: Move this to separate thread later... but for now listen for wizard events

        self.thread = Thread(target = self.listen_to_wizard_events)
        self.thread.deamon = True
        self.thread.start()


    def listen_to_wizard_events(self):
        mq = MessageQueue()
        mq.bind_queue(
            exchange='wizard', routing_key='action.*', callback=callback
        )


        # Callback for wizard events. map to furhat actions

        def callback(_mq, get_shifted_time, routing_key, msg):
            action = routing_key.rsplit('.', 1)[1]
            print(msg)
            if action == 'say':
                pass
                #self.say(msg['text'])
            if action == 'accuse':
                #location = self.environment.get_participants(msg['participant']).get_furhat_angle()
                #self.gaze_at(location)
                # self.say('I accuse you')
                pass
            if action == 'defend':
                #location = self.environment.get_participants(msg['participant']).get_furhat_angle()
                #self.gaze_at(location)
                # self.say('I accuse you')
                pass
            if action == 'support':
                #location = self.environment.get_participants(msg['participant']).get_furhat_angle()
                #self.gaze_at(location)
                # self.say('I accuse you')
                pass
        print('[*] Waiting for messages. To exit press CTRL+C')
        mq.listen()


    def say(self, text):
        with connect_to_iristk(self.FURHAT_IP) as furhat_client:
            furhat_client.say(self.FURHAT_AGENT_NAME, text)

    def gaze_at(self, location):
        with connect_to_iristk(self.FURHAT_IP) as furhat_client:
            furhat_client.gaze(self.FURHAT_AGENT_NAME, location)

a = Agent(None)
