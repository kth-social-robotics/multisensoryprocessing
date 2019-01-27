There are three main components to the multi sensory processing framework named farmi.


There are publishers, which publish data; there are subscribers which subscribe to data and there is a directory service where publishers register themselves so that subscribers can find them.

Below a minimal example is shown:

`directory_service.py` (or just run `farmi-server`)
```
from farmi import DirectoryService
ds = DirectoryService()
ds.listen()
```

`receiver.py`
```
from farmi import Subscriber

def fn(msg):
    print(msg)

s = Subscriber('some_topic', fn)
s.listen()
```

`sender.py`
```
import time
from farmi import Publisher
pub = Publisher('some_topic')
time.sleep(1)

for i in range(10):
    pub.send((i, "hello!"))

pub.close()
```
