from furhat import connect_to_iristk
from time import sleep

FURHAT_IP = '130.237.67.115' # Furhat IP address
FURHAT_AGENT_NAME = 'system' # Furhat agent name. Can be found under "Connections" in the furhat web-GUI

with connect_to_iristk(FURHAT_IP) as furhat_client:
    #def event_callback(event):
        #print(event) # Receives each event the furhat sends out.

    # Listen to events
    #furhat_client.start_listening(event_callback) # register our event callback receiver

    # Speak
    furhat_client.say(FURHAT_AGENT_NAME, 'hello humans')

    # Head Limits
    # X from -1 (right) to +1 (left)
    # Y from -1 (down) to +1 (up)
    # Z from 0 to 2 (forwards)
    # Gaze can go further

    # Ranges X
    MocapMaxx = -1.82
    MocapMinx = -3.23
    MocapRangex = (MocapMaxx - MocapMinx)
    FurhatMaxx = 3
    FurhatMinx = -2
    FurhatRangex = (FurhatMaxx - FurhatMinx)

    # Ranges Y
    MocapMaxy = 1.70
    MocapMiny = 0.75
    MocapRangey = (MocapMaxy - MocapMiny)
    FurhatMaxy = 1
    FurhatMiny = -1
    FurhatRangey = (FurhatMaxy - FurhatMiny)

    # Calculate Furhat values based on Mocap values
    MocapValuex = -3.21
    FurhatValuex = (((MocapValuex - MocapMinx) * FurhatRangex) / MocapRangex) + FurhatMinx
    MocapValuey = 1.20
    FurhatValuey = (((MocapValuey - MocapMiny) * FurhatRangey) / MocapRangey) + FurhatMiny

    furhat_client.gaze(FURHAT_AGENT_NAME, {'x': FurhatValuex, 'y': FurhatValuey,'z': 2.00})
    sleep(0.01)

    # Continuous gaze
    # for i in range(10,-10,-1):
    #     furhat_client.gaze(FURHAT_AGENT_NAME, {'x':i/10,'y':i/10,'z':2.00})
    #     sleep(0.1)

    furhat_client.say(FURHAT_AGENT_NAME, 'I gazed')
    sleep(0.01)
