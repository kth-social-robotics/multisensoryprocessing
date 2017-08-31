# import fatima
from furhat import connect_to_iristk
import pika
# from .. import Player
from threading import Thread
import json
import sys,os,re
import random
import csv
sys.path.append('..')
import Environment
sys.path.append('../..')
from shared import MessageQueue
# etc..


class Agent(object):
    """docstring for Agent."""

    FURHAT_IP = '192.168.0.117'
    FURHAT_AGENT_NAME = 'furhat6'
    RABBITMQ_CONNECTION = {'host': 'localhost', 'port': 32777}
    FURHAT_HOME = '/Users/jdlopes/enterface17/'

    def __init__(self, environment):
        super(Agent, self).__init__()
        self.environment = environment

        # TODO: Move this to separate thread later... but for now listen for wizard events

        self.thread = Thread(target = self.listen_to_wizard_events)
        self.thread.deamon = True
        self.thread.start()
        self.fatima_mq = MessageQueue('fatima_agent')
        self.gaze_at({'x':0,'y':0,'z':1})
        self.prompts_dict = self.load_prompts()


    def load_prompts(self):
        prompts_dict = {}
        for root,dir,files in os.walk(os.path.join(self.FURHAT_HOME,'NLG/wizard/')):
            for file in files:
                if file.endswith('.prompts'):
                    with open(os.path.join(root,file),'r') as prompt_file:
                        if not file.split('.prompts')[0] in prompts_dict:
                            prompts_dict[file.split('.prompts')[0]] = []
                        for row in csv.reader(prompt_file,delimiter=';'):
                            try:
                                #print(row[1])
                                prompts_dict[file.split('.prompts')[0]].append(row[1])
                            except:
                                print(row)
        return prompts_dict


    def listen_to_wizard_events(self):
        mq = MessageQueue('wizard_listener')

        #getting system prompts
        spoken_prompt_list = []

        def get_prompt(action, participant=None):

            if participant == 'general' and action != 'accuse':
                selected_prompt = random.choice(self.prompts_dict['%s.general' % action])
                while selected_prompt in spoken_prompt_list:
                    selected_prompt = random.choice(self.prompts_dict['%s.general' % action])
            elif participant == 'self':
                selected_prompt = random.choice(self.prompts_dict['%s.self' % action])
                while selected_prompt in spoken_prompt_list:
                    selected_prompt = random.choice(self.prompts_dict['%s.self' % action])
            else:
                selected_prompt = re.sub('<user_id>', participant, random.choice(self.prompts_dict['%s.user' % action]))
                while selected_prompt in spoken_prompt_list:
                    selected_prompt = re.sub('<user_id>', participant, random.choice(self.prompts_dict['%s.user' % action]))

            try:
                return selected_prompt
            except:
                print('no prompt available')
                return False

        def get_prompt_action(action):

            selected_prompt = random.choice(self.prompts_dict['%s'%action])
            while selected_prompt in spoken_prompt_list:
                selected_prompt = random.choice(self.prompts_dict['%s'%action])
            return selected_prompt

        # Callback for wizard events. map to furhat actions
        def callback(_mq, get_shifted_time, routing_key, body):
            #print(routing_key)
            action = routing_key.rsplit('.', 1)[1]
            msg = body
            furhat_class = self.environment.get_participant('red')
            if action == 'say':
                self.say(msg['text'])
            if action == 'gesture':
                self.gesture(msg['gesture_name'])
            if action == 'accuse':
                if msg['participant'] != 'general':
                    if get_prompt(action,msg['participant']):
                        self.say(get_prompt(action,msg['participant']))
                        addressee = self.environment.get_participant(msg['participant'])
                        furhat_class.gaze = addressee.get_furhat_angle()
                        #location = addressee
                        self.gaze_at(furhat_class.gaze)

            if action == 'defend':
                defend_prompt = get_prompt(action,msg['participant'])
                print(msg['participant'])
                if defend_prompt:
                    spoken_prompt_list.append(defend_prompt)
                    self.say(defend_prompt)
                    if random.choice(['last_speaker','defendee']) == 'last_speaker':
                        self.gaze_at({'x':0,'y':0,'z':1})
                        furhat_class.gaze = {'x':0,'y':0,'z':1}
                    else:
                        furhat_class.gaze = self.environment.get_participant(msg['participant']).get_furhat_angle()
                        self.gaze_at(furhat_class.gaze)

            if action == 'support':
                support_prompt = get_prompt(action,msg['participant'])
                if support_prompt:
                    spoken_prompt_list.append(support_prompt)
                    self.say(support_prompt)
                if msg['participant'] == 'general':
                    furhat_class.gaze = {'x':0,'y':0,'z':1}
                    self.gaze_at(furhat_class.gaze)
                else:
                    furhat_class.gaze = self.environment.get_participant(msg['participant']).get_furhat_angle()
                    self.gaze_at(furhat_class.gaze)

            if action == 'vote':
                vote_prompt = get_prompt(action,msg['participant'])
                if vote_prompt:
                    spoken_prompt_list.append(vote_prompt)
                    self.say(vote_prompt)
                    furhat_class.gaze = self.environment.get_participant(msg['participant']).get_furhat_angle()
                    self.gaze_at(furhat_class.gaze)

            if action == 'small_talk':
                small_talk_prompt = get_prompt(action,msg['participant'])
                if small_talk_prompt:
                    spoken_prompt_list.append(small_talk_prompt)
                    self.say(small_talk_prompt)
                    if msg['participant'] != 'general':
                        furhat_class.gaze = self.environment.get_participant(msg['participant']).get_furhat_angle()
                        self.gaze_at(furhat_class.gaze)
                    else:
                        furhat_class.gaze = {'x':0,'y':0,'z':1}
                        self.gaze_at(furhat_class.gaze)

            if action == 'summary':
                summary_prompt = get_prompt_action('summary')
                self.say(summary_prompt)
                spoken_prompt_list.append(summary_prompt)
                furhat_class.gaze = {'x':0,'y':0,'z':1}
                self.gaze_at(furhat_class.gaze)

            if action == 'backchannel':
                backchannel_prompt = get_prompt_action('backchannel')
                self.say(backchannel_prompt)

            if action == 'get_vote':
                self.get_vote_suggestion()

            self.update_belief()

        mq.bind_queue(
            exchange='wizard', routing_key='action.*', callback=callback
        )

        print('[*] Waiting for messages. To exit press CTRL+C')
        mq.listen()

    def update_belief(self):

        env.update_accusal_data()
        for player in self.environment.get_participants():
            if 'belief_is_werewolf' not in player.properties:
                player.properties['belief_is_werewolf'] = 0.0

            self.fatima_mq.publish(
                exchange='fatima',
                routing_key='belief_update',
                body={'participant': player.name,
                      'belief': player.properties['belief_is_werewolf']},
                no_time=True
            )

    def get_suggest_action(self):
        '''
        gets the list
        :return:
        '''

        suggested_action = 'accuse pink'
        #suggested_action = get_fatima_action(env)

        self.fatima_mq.publish(
            exchange='fatima_agent',
            routing_key='suggest_action',
            body = {'action':suggested_action}
        )

    def get_vote_suggestion(self):
        '''
        gets suggestion for the voting round from fatima

        :return:
        '''
        accusal_data = env.update_accusal_data()
        if accusal_data != '':
            #if there is an accusal available send it
            self.fatima_mq.publish(
                exchange='fatima',
                routing_key='suggest_vote',
                body={'participant' : accusal_data}
                #body={'participant': 'pink'}
            )

    def say(self, text):
        with connect_to_iristk(self.FURHAT_IP) as furhat_client:
            furhat_client.say(self.FURHAT_AGENT_NAME, text)

    def gaze_at(self, location):
        with connect_to_iristk(self.FURHAT_IP) as furhat_client:
            furhat_client.gaze(self.FURHAT_AGENT_NAME, location)

    def gesture(self, gesture_name):
        with connect_to_iristk(self.FURHAT_IP) as furhat_client:
            furhat_client.gesture(self.FURHAT_AGENT_NAME, gesture_name)

env = Environment.Environment()
a = Agent(env)
