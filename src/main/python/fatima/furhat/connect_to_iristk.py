import socket
from contextlib import contextmanager
from .iristk_client import IristkClient


IRISTK_DEFUALT_PORT = 1932
DEFAULT_CLIENT_NAME = 'furhat_over_network'
DEFAULT_EVENTS_TO_SUBSCRIBE_TO = '**' # could be one or more specific events, e.g. sense.speech.rec


@contextmanager
def connect_to_iristk(host=None, client_name=DEFAULT_CLIENT_NAME, port=IRISTK_DEFUALT_PORT,
                      subscribe_to=DEFAULT_EVENTS_TO_SUBSCRIBE_TO, debug=False):
    ''' Here we connect to Iristk and return an instance of an iristk client'''
    furhat_client = None
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        data = ''
        client.send('CONNECT furhat {}\n'.format(client_name).encode('UTF-8'))
        while True:
            packet = client.recv(1)
            if not packet:
                # The socket has been closed.
                break
            data += packet.decode()
            if '\n' in data:
                line, data = data.split('\n', 1)
                if debug:
                    print(line)
                if line == 'CONNECTED':
                    client.send('SUBSCRIBE {}\n'.format(subscribe_to).encode())
                    break
        furhat_client = IristkClient(client, client_name)
        yield furhat_client
    finally:
        if furhat_client:
            furhat_client.disconnect()
