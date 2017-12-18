import zmq
import socket

def create_zmq_server():
    # Get ip
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()

    # Set up zmq server
    context = zmq.Context()
    s = context.socket(zmq.PUB)
    zmq_port = s.bind_to_random_port('tcp://*', max_tries=150)
    zmq_server_addr = 'tcp://{}:{}'.format(ip, zmq_port)

    return s, zmq_server_addr
