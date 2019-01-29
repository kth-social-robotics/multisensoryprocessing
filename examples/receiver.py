from farmi import Subscriber

def fn(msg):
    print(msg)

s = Subscriber('some_topic', fn)
s.listen()
