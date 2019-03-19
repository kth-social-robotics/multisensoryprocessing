from farmi import Subscriber


def fn(msg):
    print(msg)


s = Subscriber()
s.subscribe_to("some_topic", fn)
s.listen()
