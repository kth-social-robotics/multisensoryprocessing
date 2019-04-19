import socket

from farmi.serialization import deserialize_file


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def read_farmi_file(filename):
    with open(filename, "rb") as f:
        for value in deserialize_file(f):
            yield value
