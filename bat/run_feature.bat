REM CMD /K CALL "run_feature.bat"

REM start feature processor
START CMD /K CALL "featureprocessor.bat"

REM delay for 15 seconds
CHOICE /N /C YN /T 15 /D Y >NUL

REM start mocapgaze processor
START CMD /K CALL "mocapgazeprocessor.bat"

REM delay for 15 seconds
CHOICE /N /C YN /T 15 /D Y >NUL

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
