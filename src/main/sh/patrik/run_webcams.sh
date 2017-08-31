# REM start python webcam sensor blue
# START CMD /K CALL "run_video-blue.bat"
#
# REM start python webcam sensor brown
# START CMD /K CALL "run_video-brown.bat"
#
# REM start python webcam sensor white
# START CMD /K CALL "run_video-white.bat"
cd ../../python/sensors/video/
python video_test.py blue &
python video_test.py brown &
python video_test.py white &
