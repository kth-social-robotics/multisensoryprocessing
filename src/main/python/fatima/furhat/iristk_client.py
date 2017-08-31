import json
import uuid
from threading import Thread


class IristkClient(object):

    def __init__(self, client, client_name, callback=None):
        self.client = client
        self.client_name = client_name
        self._is_listening = False

    def start_listening(self, callback):
        self._is_listening = True
        thread = Thread(target=self.socket_listener, args=(self.client, callback))
        thread.deamon = True
        thread.start()

    def socket_listener(self, client, callback):
        data = ''
        while self._is_listening:
            packet = client.recv(1)
            if not packet:
                # The socket has been closed.
                break
            data += packet.decode()
            if '\n' in data:
                line, data = data.split('\n', 1)
                try:
                    json_data = json.loads(line)
                    callback(json_data)
                except ValueError:
                    pass

    def disconnect(self):
        self._is_listening = False
        if self.client:
            self.client.send('CLOSE\n'.encode())

    def attend_user(self, agent, user):
        self._send_event('action.attend', agent, {'target': user})

    def attend_nobody(self, agent):
        self._send_event('action.attend', agent, {'target': 'nobody'})

    def attend_all(self, agent):
        self._send_event('action.attend.all', agent, {})

    def attend_location(self, agent, location, mode='default'):
        self._send_event('action.attend', agent, {'location': location, 'mode': mode})

    def gaze(self, agent, location, mode='default'):
        self._send_event('action.gaze', agent, {'location': location, 'mode': mode})

    def gesture(self, agent, gesture_name):
        self._send_event('action.gesture', agent, {'name': gesture_name})

    def say(self, agent, text, audio_file=None, abort=True):
        event_data = {'text': text, 'abort': abort}
        if audio_file:
            event_data['audio'] = audio_file
        self._send_event('action.speech', agent, event_data)

    def _send_event(self, event_name, agent, specialised_event):
        event = {
            'class': 'iristk.system.Event',
            'event_name': event_name,
            'agent': agent,
            'event_sender': self.client_name,
            'event_id': str(uuid.uuid1())
        }
        event.update(specialised_event)
        event_msg = '{}\n'.format(json.dumps(event)).encode('utf8')
        self.client.send('EVENT {} {}\n'.format(event_name, len(event_msg)).encode())
        self.client.send(event_msg)
