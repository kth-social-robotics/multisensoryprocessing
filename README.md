Multisensory Processing Architecture

Misc:
-Time server: keeps a global time stamp for all devices
-Processor and sensor loggers: logs the streams to file

Processors:
-Feature vector: gathers data from mocap_gaze processor and nlp processor and creates feature
-Mocap Gaze: gathers streams from mocap and tobii and aligns the data
-NLP: gathers data from ASR and parses with syntaxnet

Pre-Processors:
-Mocap: gathers data from mocap stream and creates rigid bodies
-Tobii: gathers data from tobii stream and creates participant data
-ASR: gathers data from microphone and runs watson asr

Sensors:
-Mocap: gathers mocap steram
-Tobii: gathers tobii stream
-Microphone: gathers microphone stream

Other:
-Visualisation: gets data from mocap_gaze processor and visualises the objects
-ROS connector: sends feature vector to the ROS server

Starting sequence:
-Git sync (both mac and win)
-Settings (both mac and win)
-RabbitMQ (win)
-Timeserver (win)
    -Logging of processors (win) (optional)
    -Logging of sensors (win) (optional)
-ROS Connector (Server) (mac) (optional)

-NLP Bat:
    -Microphone (win)

-Feature Vector (mac)
-Mocap-gaze processor (mac)
-Visualisation (win)
-Mocap pre-processor (win)
-Mocap sensor (win)
-NLP (mac)
-Tobii pre-processor (win)
-ASR (win)
-Tobii sensor x2 (win)
