Multisensory Processing Architecture

Misc:
-Time server: keeps a global time stamp for all devices
-Processor and sensor loggers: logs the streams to file

Processors:
-Feature vector: gathers data from mocap_gaze processor and nlp processor and creates feature
-Mocap Gaze: gathers streams from mocap and tobii and aligns the data
-NLP: gathers data from ASR and parses with syntaxnet or with predetermined grammar

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
-Git sync (pmil, mac)
-Settings
-RabbitMQ (pmil)
-Timeserver (pmil)

-WebGL Visualisation browser (mac) (optional)
    -Run mocapgaze process separately
    -Define pointing markers for gloves
    -Define number of glasses, gloves and targets
    -Open MAMP and Firefox


+Furhat bat (pmil)


-Feature bat (pmil):
    -Feature vector bat (pmil)
        -Define glasses and hands markers
        -Define mic for P1
        -Define number of targets, glasses, gloves and tables
    -Mocap-gaze processor bat (pmil)
        -Define Tobii markers and head angle on Matlab
    -Tobii pre-processor bat (pmil)
    -Mocap pre-processor bat (pmil)
        -Update mocap objects
    -Mocap sensor bat (pmil)

-NLP sh (mac):
    -NLP processor sh (mac)
    -ASR sh (mac)
    -Microphone sh (mac)

-Tobii glasses1 (pmil)
