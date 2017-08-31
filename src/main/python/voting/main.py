from flask import Flask, render_template, request
import pika
import json
import yaml
import sys
import os
sys.path.append('..')
from shared import MessageQueue

SETTINGS_FILE = os.path.abspath(
    os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, 'settings_local.yaml')
)
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())


app = Flask(__name__)
mq = MessageQueue("voting-app")
#mq = MessageQueue('voting')

@app.route("/vote")
def vote():
    participant = request.args.get('participant')
    if participant:
        mq.publish(
            exchange=settings['messaging']['environment'],
            routing_key='action.vote.{}'.format(participant),
            body={'participant': participant,
                  'last_vote': request.args.get('vote_for', '')},
            no_time=True
        )
        return 'OK'
    else:
        return 'NOT_OK'

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)
