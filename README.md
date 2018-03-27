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
-Furhat: sends gaze and speech data to furhat
-Instructions: Instructions UI and feedback
-Visualisation: gets data from mocap_gaze processor and visualises the objects
-ROS connector: sends feature vector to the ROS server

Starting sequence:
-Git sync (macdimos, macjocke, pmil, gigabyte)
-Settings
-RabbitMQ (pmil)
-Timeserver (pmil)
    -Logging of processors (pmil) (optional)
    -Logging of sensors (pmil) (optional)

+++-Attention model (Server) (mac)
    +++-Define server IP on server and client files and feature bat file
    +++-Get log files
    +++-Define objects and tables
+++-Instructions (mac):
    +++-Define server IP
+++-Processors sh (mac):
    +++-Feature Vector sh (mac)
        +++-Define glasses and hands markers
        -Define Furhat IP
        -Define mic for P1 and P2
        -Define number of targets, glasses, gloves and tables

-WebGL Visualisation browser (mac)
    -Run mocapgaze process separately
    -Define pointing markers for gloves
    -Define number of glasses, gloves and targets
    -Open MAMP and Firefox

-Mocapgaze bat (pmil):
    -Mocap-gaze processor bat (pmil)
        -Define Tobii markers and head angle on Matlab
    -Tobii pre-processor bat (pmil)
    -Mocap pre-processor bat (pmil)
        -Update mocap objects
    -Mocap sensor bat (pmil)
-Tobii glasses1 (pmil)
-Tobii glasses2 (pmil)
-NLP sh (macjocke):
    -NLP processor sh (macjocke)
    -ASR sh (macjocke)
    -Microphone sh (macjocke)
    -Microphone sh (macjocke)
