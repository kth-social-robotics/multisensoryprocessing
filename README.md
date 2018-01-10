# Multi-sensory processing


## Install & Setup
run ```pip install -r requirements``` in order to install the basic requirements.

run ```python misc/time_server.py``` in order to start the time server.
run ```python misc/disk_logger.py``` for a process that logs all of the raw sensor data to disc.

## Components

- Sensors
- Pre-processors
- Processors
- Misc
  - Rabbit mq
  - Time server

#### Sensors
Sensors are responisble for passing raw sensor data to the reset of the system. Any process requiring this raw data can then suscribe to the data stream and do the processing required.

#### Pre-processors
A pre-processor subscribes to a sensor and chunks up the data into more managable pieces and sends them out as events. As data streams can be quiet heavy, it is not advided to send them directly as events, and instead pass them through a pre-processor which aggregates and prunes the data for one or more processors who are interested in processing this data.

#### Processors
Processors receive events with data, processes them (e.g. a gaze-tracking processor would calculate who is currently looking at who from the raw eye-tracking data).

#### Time server
The time server lets all of the components of the system have a centralized time, so that synchronization of data streams is possible. 

The time server can be started running the time_server.py that can be found in the misc folder of the python source code.

#### Messaging
Messaging is done with rabbitmq, but as such another message broker could be used. 

Install rabbitmq from Docker (Suggestion):
  - Check if you have Docker installed. 
  - Once docker is installed you can install the rabbitmq docker running the following command from your terminal :`docker pull rabbitmq`.
  - Start the rabbitmq docker using the following command: `docker run -d -p [<port>:<port>] rabbitmq[:latest]`.

  Please refer to the rabbitmq docker documentation for the complete specification (https://hub.docker.com/_/rabbitmq/)
  
## Architecture

The system is built to be distributed over several machines. And having stand-alone applications running on each maching focusing on performing some kind of work.

