# python3 polly.py

import boto3
from boto3 import client
from playsound import playsound
from websocket import create_connection
import json

# Connect to Amazon Polly
polly_client = boto3.Session(
    aws_access_key_id = "AKIAJZ3IUTAZPQIIBW4A",
    aws_secret_access_key = "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",
    region_name='us-west-2').client('polly')

# Sunthesis
response = polly_client.synthesize_speech(
    VoiceId='Joanna',
    OutputFormat='mp3',
    Text = "<speak>I already told you I <emphasis level='strong'>really</emphasis> like that person.</speak>",
    TextType = "ssml")

# Save to file
file = open('speech.mp3', 'wb')
file.write(response['AudioStream'].read())
file.close()

# Speak
playsound('speech.mp3')

# Furhat
ws = create_connection("ws://130.237.67.157:80/api")
ws.send(
    json.dumps({"event_name": "furhatos.event.actions.ActionSpeech", "text": "I already told you I <emphasis level='strong'>really</emphasis> like that person."})
)
