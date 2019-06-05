REM START CMD /K CALL "run_mocapgaze.bat"

REM start mocapgaze processor
REM START CMD /K CALL "mocapgazeprocessor.bat"

REM delay for 10 seconds
REM CHOICE /N /C YN /T 10 /D Y >NUL

REM start tobii preprocessor
REM START CMD /K CALL "tobiipreprocessor.bat"

REM delay for 2 seconds
REM CHOICE /N /C YN /T 2 /D Y >NUL

REM start mocap preprocessor
REM START CMD /K CALL "mocappreprocessor.bat"

REM delay for 2 seconds
REM CHOICE /N /C YN /T 2 /D Y >NUL

REM start mocap sensor
START CMD /K CALL "mocapsensor.bat"

EXIT
