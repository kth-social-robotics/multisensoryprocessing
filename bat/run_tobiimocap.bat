REM START CMD /K CALL "run_tobiimocap.bat"

REM start tobii preprocessor
START CMD /K CALL "tobiipreprocessor.bat"

REM delay for 2 seconds
CHOICE /N /C YN /T 2 /D Y >NUL

REM start mocap preprocessor
START CMD /K CALL "mocappreprocessor.bat"

REM delay for 2 seconds
CHOICE /N /C YN /T 2 /D Y >NUL

REM start mocap sensor
START CMD /K CALL "mocapsensor.bat"

EXIT
