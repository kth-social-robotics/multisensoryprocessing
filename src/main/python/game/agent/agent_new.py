# import fatima
from furhat import connect_to_iristk
import pika
# from .. import Player
from threading import Thread
import json,csv
import os,re
import random
# etc..


class Agent(object):
    """docstring for Agent."""

    FURHAT_IP = '192.168.0.117'
    FURHAT_AGENT_NAME = 'furhat6'
    RABBITMQ_CONNECTION = {'host': '192.168.0.108', 'port': 32777}
    FURHAT_HOME = '/Users/jdlopes/enterface17/'

    def __init__(self, environment):
        super(Agent, self).__init__()
        self.environment = environment

        # TODO: Move this to separate thread later... but for now listen for wizard events

        self.thread = Thread(target = self.listen_to_wizard_events)
        self.thread.deamon = True
        self.thread.start()


    def listen_to_wizard_events(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(**self.RABBITMQ_CONNECTION))
        channel = connection.channel()
        channel.exchange_declare(exchange='wizard', type='topic')
        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange='wizard', queue=queue_name, routing_key='action.*')

        prompts_dict = {}

        for root,dir,files in os.walk(os.path.join(FURHAT_HOME,'NLG/wizard/')):
            for file in files:
                if file.endswith('.prompts'):
                    print file.split('.prompts')[0]
                    with open(os.path.join(root,file),'r') as prompt_file:
                        if not prompts_dict.has_key(file.split('.prompts')[0]):
                            prompts_dict[file.split('.prompts')[0]] = []
                        for row in csv.read(prompt_file,delimiter=','):
                            prompts_dict[file.split('.prompts')[0]].append(row)


        # Callback for wizard events. map to furhat actions
        def callback(ch, method, properties, body):
            action = method.routing_key.rsplit('.', 1)[1]
            msg = json.loads(body)
    #        if action == 'say':
    #            self.say(msg['text'])
            if action == 'accuse':
                self.say(get_prompt(action,prompts_dict,msg['participant']))
                location = self.environment.get_participants(msg['participant']).get_furhat_angle()
                self.gaze_at({'x': 2, 'y': 0, 'z': 2})
            if action == 'defend':
                self.say(get_prompt(action,prompts_dict,msg['participant']))
            if action == 'support':
                self.say(get_prompt(action,prompts_dict,msg['participant']))

        def get_prompt(action,prompts_dict,participant = None):

            if participant == None:
                return random.choice(prompts_dict['%s.gerenal'%action])
            elif participant == 'self':
                return random.choice(prompts_dict['%s.self'%action])
            else:
                return re.sub('<user_id>',participant,random.choice(prompts_dict['%s.user'%action]))


        channel.basic_consume(callback, queue=queue_name)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    def say(self, text):
        with connect_to_iristk(self.FURHAT_IP) as furhat_client:
            furhat_client.say(self.FURHAT_AGENT_NAME, text)

    def gaze_at(self, location):
        with connect_to_iristk(self.FURHAT_IP) as furhat_client:
            furhat_client.gaze(self.FURHAT_AGENT_NAME, location)

a = Agent(None)
