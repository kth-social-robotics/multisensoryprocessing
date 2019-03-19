import time

from farmi import Publisher

pub = Publisher("some_topic")
time.sleep(1)

for i in range(10):
    pub.send((i, "hello!"))

pub.close()
