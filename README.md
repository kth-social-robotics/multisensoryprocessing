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

-Attention model (Server) (mac)
-ROS Connector (Server) (mac) (optional)

-Processors sh (mac):
    -Feature Vector sh (mac)
    -NLP processor sh (mac)
    -Mocap-gaze processor sh (mac)
-WebGL Visualisation browser (win)
-TobiiMocap bat (win):
    -Tobii pre-processor bat (win)
    -Mocap pre-processor bat (win)
    -Mocap sensor bat (win)
-Tobii glasses1 (win)
-Tobii glasses2 (win)
-ASR bat (win):
    -ASR bat (win)
    -Microphone bat (win)
