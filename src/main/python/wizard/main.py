from flask import Flask, render_template, request
import pika
import json
import sys
import random
from threading import Thread
from flask_socketio import SocketIO, send, emit
sys.path.append('..')
from shared import create_zmq_server, MessageQueue


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
mq = MessageQueue('wizard')


@socketio.on("say")
def handle_say(json):
    mq.publish(
        exchange='wizard',
        routing_key='action.say',
        body={'text': json.get('text', '')},
        no_time=True
    )

@app.route('/say')
def say():
    mq.publish(
        exchange='wizard',
        routing_key='action.say',
        body={'text': request.args.get('text', '')},
        no_time=True
    )
    return 'OK'

@app.route('/dialog_act')
def accuse():
    action = request.args.get('action')
    print(action)
    if action:
        mq.publish(
            exchange='wizard',
            routing_key='action.{}'.format(request.args.get('action')),
            body={'participant': request.args.get('participant', '')},
            no_time=True
        )
        return 'OK'
    return 'NOT_OK'

@app.route('/gesture')
def gesture():
    mq.publish(
        exchange='wizard',
        routing_key='action.gesture',
        body={'gesture_name' : request.args.get('gesture_name','')},
        no_time=True
    )
    return 'OK'


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/vote")
def vote():
    mq.publish(
        exchange='wizard',
        routing_key='action.get_vote',
        body={'participant' : request.args.get('paticipant','')},
        no_time=True
    )
    return 'OK'



@app.route("/visualizations")
def visualizations():
    return render_template('visualizations.html')

def run():
    print('I am running in my own thread!')

    #fatima_listner_mq = MessageQueue('fatima_listener')

    def update_belief_interface(msg):
        participant = msg['participant']
        belief = msg['belief']
        # print(participant,belief)
        socketio.emit('update_belief_interface', {'participant': participant, 'belief': belief})

    def display_suggested_action(msg):
        # print(msg['action'])
        socketio.emit('display_suggested_action', {'action': msg['action']})

    def display_suggested_vote(msg):
        print(msg['participant'])
        socketio.emit('display_suggested_vote', {'participant': msg['participant']})

    def update_wizard(_mq, get_shifted_time, routing_key, body):

        print('going to update wizard {}'.format(routing_key))

        action = routing_key
        msg = body

        if action == 'belief_update':
            update_belief_interface(msg)

        if action == 'suggest_action':
            display_suggested_action(msg)

        if action == 'suggest_vote':
            display_suggested_vote(msg)


    mq.bind_queue(
        exchange='fatima', routing_key='*', callback=update_wizard
    )

    print('[*] Waiting for fatima\'s messages. To exit press CTRL+C')
    mq.listen()

if __name__ == "__main__":
    thread = Thread(target=run)
    thread.deamon = True
    thread.start()
    socketio.run(app, host='0.0.0.0', debug=True, threading=True, async_mode='gevent')

