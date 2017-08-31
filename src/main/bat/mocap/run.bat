REM start timeserver
START CMD /K CALL "run_timeserver.bat"

REM start mocap sensor
REM START CMD /K CALL "mocap.bat"

REM start python webcam sensors
REM CALL "run_webcams.bat"

REM start mocap preprocessor
START CMD /K CALL "mocap_preprocessor.bat"

REM start asr preprocessor
REM START CMD /K CALL "run_asr.bat"

REM start facial features processor
START CMD /K CALL "run_facialfeatures.bat"

REM start position processor
START CMD /K CALL "run_position.bat"

REM start tobii blue sensor
REM START CMD /K CALL "run_tobii-blue.bat"

REM start tobii brown sensor
START CMD /K CALL "run_tobii-brown.bat"

REM start tobii white sensor
REM START CMD /K CALL "run_tobii-white.bat"
