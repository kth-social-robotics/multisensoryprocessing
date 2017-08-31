import pika,os,sys
from furhat import connect_to_iristk
from Player import Player
from Game import Game
from ruamel import yaml
sys.path.append('../../fatima/')
from FAtiMA import DecisionMaking
sys.path.append('../..')
from shared import MessageQueue
from threading import Thread
import operator,json


HOST = '192.168.0.100'
PORT = 32777


class Environment(object):

    FURHAT_AGENT_NAME = 'furhat6'
    FURHAT_IP = '192.168.0.117'
    FURHAT_HOME = "/Users/jdlopes/enterface17/src/main/python/"
    SETTINGS_FILE = os.path.join(FURHAT_HOME,'settings_local.yaml')

    def __init__(self):
        self.thread = Thread(target = self.listen_env)
        self.thread.deamon = True
        self.thread.start()
#        self.mq = MessageQueue("environment")

        self.settings = self._init_settings(Environment.SETTINGS_FILE)
        self.participants = Player.create_players(self.settings['players'])
        self.fatima = DecisionMaking()
        #self._init_subscription()
        self.game = None
        self.speaking_queue = []
        #self.listen_env()

    @staticmethod
    def _init_settings(settings_file):
        try:
            return yaml.safe_load(open(settings_file, 'r').read())
        except:
            raise IOError("An error has occurred while trying to load settings file.")

    def get_participant(self, participant_name):
        try:
            return [x for x in self.participants if x.name == participant_name][0]
        except:
            return ''

    def get_participants(self):
        return self.participants

    def update_accusal_data(self):
        accusals = self.fatima.get_accusals()
        if accusals != 'No accusals':
            suspect, probabilities = accusals
            for player in self.participants:
                if player.name in probabilities:
                    player.properties['belief_is_werewolf'] = probabilities[player.name]
       #     print('{} is the werewolf'.format(suspect))
            return suspect
        else:
            #default behavior when there is no decision available in FAtiMA
            for player in self.participants:
                player.properties['belief_is_werewolf'] = 0.0
            return ''


    def listen_env(self):
        mq = MessageQueue("environment")
#        print('started ')

        def event_handler(_mq, get_shifted_time, routing_key, body):
            action = routing_key.rsplit('.')[1]
            msg = body
            participant = self.get_participant(msg['participant'])

            if participant != '':

                if action == 'vote':
                    participant.last_vote = msg['last_vote']
                    self.fatima.update_vote(participant)

                if action == 'speech_active':
                    if participant not in self.speaking_queue:
                        self.speaking_queue.append(participant)
                    if self.get_participant('red').gaze != self.speaking_queue[0]:
                        self.get_participant('red').gaze = self.speaking_queue[0]
                        self.gaze_at(self.speaking_queue[0].get_furhat_angle())

                if action == 'end_of_speech':
                    if participant in self.speaking_queue:
                        self.speaking_queue.remove(participant)
                    if self.speaking_queue:
                        if self.speaking_queue[0] != self.get_participant('red').gaze:
                            self.get_participant('red').gaze = self.speaking_queue[0]
                            self.gaze_at(self.speaking_queue[0].get_furhat_angle())
                    else:
                        self.gaze_at({'x':0,'y':0,'z':1})
                        self.get_participant('red').gaze = {'x':0,'y':0,'z':1}
                    if len(self.speaking_queue) == 0:
                        print('everybody is quiet')
                        self.update_accusal_data()

                if action == 'dialogue_act':
                    participant,dialogue_act,target = self.process_dialog_acts(msg['participant'],msg['dialogue-acts'])
                    if target != '':
                        self.fatima.action_event(participant,dialogue_act,target)
            else:
                print('no participant specificied')


        mq.bind_queue(
            exchange=self.settings['messaging']['environment'], routing_key='action.*.*', callback=event_handler
        )

        print('[*] Waiting for environment messages. To exit press CTRL+C')
        mq.listen()

#    def update_fatima_knowledge_base(self):
 #       '''
 #       updates the fatima knowledge base for each player
  #      :return:
  #      '''
  #      for player in self.participants:
  #          self.fatima.update_knowledge_base(player.name)



    def start_game(self, game=None):
        self.game = game if game and isinstance(game, Game) else Game(Environment.SETTINGS_FILE)

    def process_dialog_acts(self,participant,dialogue_acts):
        '''
        get the most likely dialogue act if there is one
        otherwise returns -1

        :param participant:
        :param dialogue_acts:
        :return:
        '''
        for dialogue_act in dialogue_acts:
            most_likely_da = max(dialogue_acts[dialogue_act].items(), key=operator.itemgetter(1))
            if len(most_likely_da) == 1:
                print(participant,dialogue_act,max(most_likely_da)[0])
                return participant,dialogue_act,max(most_likely_da)[0]
            else:
                return participant,dialogue_act,''

        return participant,'',''


 #   def _init_subscription(self):
  #      print(HOST,PORT)
   #     connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST, port=PORT))
#        channel = connection.channel()

#        channel.queue_declare(queue='processors')
#        channel.basic_consume(self.process_processors_data, queue='processors', no_ack=True)

#        channel.start_consuming()

    def process_processors_data(self, ch, method, properties, body):
        print(" [x] Received %r" % body)

    def gaze_at(self, location):
        with connect_to_iristk(self.FURHAT_IP) as furhat_client:
            furhat_client.gaze(self.FURHAT_AGENT_NAME, location)


def send_message(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST, port=PORT))
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    channel.basic_publish(exchange='', routing_key='hello', body=message)
    connection.close()

