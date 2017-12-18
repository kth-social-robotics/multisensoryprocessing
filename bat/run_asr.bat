REM START CMD /K CALL "run_asr.bat"

REM start asr preprocessor
START CMD /K CALL "asr.bat"

REM delay for 2 seconds
CHOICE /N /C YN /T 2 /D Y >NUL

REM start microphone sensor
START CMD /K CALL "mic.bat"
