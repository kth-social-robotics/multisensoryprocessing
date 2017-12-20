
# FACT INTEGRATION KERNEL
The kernel ([Olov Nykvist](onykvist@kth.se)) is a node of the fact integration system operating between "The Architecture" ([TMH, Dimosthenis Kontogiorgos](diko@kth.se)), the Hololens module ([Elena Sibirtseva](elenasi@kth.se)) and the underlying ROS-network ([Hakan Karaoguz](hkarao@kth.se), [Robert Krug](rkrug@kth.se)). This README describes the state of the kernel after the integration week 2017-12-15.

### Kernel
The system is launched by calling
```python
$ python3.5 main.py -[i][s][r][da][dy]
```
Where `-i` launches the Interpreter, `-s` the Server, `-r` the Subscriber and `-da` and `-dy` the dummy-architecture and dummy-yumi respectively. These can also be combined so `-is` starts both a Interpreter and a Server-process.

### Interpreter
The interpreter's objective is to hold the attention model of the system. As of the time of writing, the attention model consists of a python list of dictionaries (`self.attention_table`). Each dictionary holds attributes of one object, as recognised by the vision system, together with information about the attention given.

The script will starts the `_print_blocks()` process, which prints the attention table every `self.print_every` second, and then enter an endless loop of waiting for and reading incomming messages from the server. It processes two types of messages: `update` and `data` which triggers the functions `_update_block_array` and `_disambiguate` respectively.

##### Update `_update_block_array()`
The following is an example of an update-message
```python
update;{"id": 7, "y": 0.25, "x": 0.23, "c": 105}$
```
allthough the order of the json does not matter. If the id in the message corresponds to an object in the attention table, the attributes of that object is updated according to the new data. If the id in the message is new, however, the new object is added to the table with `include=True`, `at=0` and `lh=0`.

##### Disambiguate `_disambiguate()`
The following is an example of an data-message is
```python
data;{"P1F": ["yes"], "P1A": ["red"], "P1V": ["pick"], "P1N": ["block"], "P1GP": [0.34, 0.12], "P1G": "T1"}$
```
None of the keys given in the above example are required and only `P1F`, `P1A` and `P1GP` are considered in the current implementation. The `P1GP` field is given as a list, of length 2, of floats that corresponds to the coordinates of the gaze. If this field is given the system will find the object in the attention table closest to the position and increase that object's `at` value by one (see **Likelihood** below). The `P1A` field is given as a list of strings containing attribute specifications given by the user. If, for example, the field value is `["red"]` all the objects in the attention table with `c:"red"` will have their `include` value changed to `True` and all the rest to `False`. If the value of `P1A` is `["red", "green"]` the objects with `c:"red"` or `c:"green"` will get `include:True` and so on. The `P1F` field is given as a list of strings containing positive or negative confirmation. If the field value of `P1F` contains the word "yes" the interpreter will pick the object with the highest likelihood and send this in an action message to the ROS-system. If it contains the word "no" the system will reset the attention table.

If, after likelihood calculations, any of the objects has a higher `lh` value than `self.likelihood_threshold` the interpreter will send an action message to the ROS-system. Note, if `self.likelihood_threshold` > 1 the only way of sending an action is by positive confirmation.

##### Likelihood `lh`
The likelihood is calculated for every object during every call to the `_disambiguate()` function. Two factors affects the likelihood value of an object; `include` and `at`. If `include` is set to `False` for an object the likelihood from include (`lh_i`) will be 0, and 1/(total number of `include:True`) otherwise. The `at` is an integer counter that indicates how many times its object has been the subject of the gaze. The likelihood for an object is thus calculated by `at`/`at_tot` * `lh_i`, and then normalized so that `lh` for all objects sum to 1.

### Dummies
The dummies are for testing and developement purposes. The YuMi dummy sends update messages to the interpreter so the interpreter can build an attention table. The architecture sends random gaze and verbal information to the interpreter.

### Server

### Subscriber
