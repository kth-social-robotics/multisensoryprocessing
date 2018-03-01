from furhat import connect_to_iristk
from time import sleep

FURHAT_IP = '130.237.67.172' # Furhat IP address
FURHAT_AGENT_NAME = 'system' # Furhat agent name. Can be found under "Connections" in the furhat web-GUI

with connect_to_iristk(FURHAT_IP) as furhat_client:
    def event_callback(event):
        print(event) # Receives each event the furhat sends out.

    # Print events
    #furhat_client.start_listening(event_callback) # register our event callback receiver

    # Speak
    furhat_client.say(FURHAT_AGENT_NAME, 'hello humans')

    # Gaze
    # X from -1 (right) to +1 (left)
    # Y from -1 (down) to +1 (up)
    # Z from 0 to 2 (forwards)
    furhat_client.gaze(FURHAT_AGENT_NAME, {'x':-1.00,'y':1.00,'z':2.00})
    sleep(0.1)

    # Continuous gaze
    for i in range(-10,10,1):
        furhat_client.gaze(FURHAT_AGENT_NAME, {'x':i/10,'y':0,'z':2.00})
        sleep(0.1)

    furhat_client.say(FURHAT_AGENT_NAME, 'I gazed')
    sleep(0.1)
