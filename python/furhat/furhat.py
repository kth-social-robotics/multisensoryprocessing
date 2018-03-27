from furhat import connect_to_iristk
from time import sleep

FURHAT_IP = '130.237.67.115' # Furhat IP address
FURHAT_AGENT_NAME = 'system' # Furhat agent name. Can be found under "Connections" in the furhat web-GUI

def convert_to_furhat_coordinates(furhat_position, object_position):
    return [ object_position[2] - furhat_position[2], object_position[1] - furhat_position[1], - (object_position[0] - furhat_position[0])]

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

    # Coordinates from mocap
    furhat_position = [-1.02193, 0.96456 + 0.2, 2.74624]
    object_position1 = [-2.74473, 0.7612, 3.37574]
    object_position2 = [-2.267, 1.152, 3.735]

    # Convert to mocap space
    object_coordinates_furhat_space = convert_to_furhat_coordinates(furhat_position, object_position1)
    print(object_coordinates_furhat_space)
    furhat_client.gaze(FURHAT_AGENT_NAME, {'x': object_coordinates_furhat_space[0], 'y': object_coordinates_furhat_space[1],'z': object_coordinates_furhat_space[2]})
    sleep(0.01)

    object_coordinates_furhat_space = convert_to_furhat_coordinates(furhat_position, object_position2)
    print(object_coordinates_furhat_space)
    furhat_client.gaze(FURHAT_AGENT_NAME, {'x': object_coordinates_furhat_space[0], 'y': object_coordinates_furhat_space[1],'z': object_coordinates_furhat_space[2]})
    sleep(0.01)

    # Continuous gaze
    # for i in range(10,-10,-1):
    #     furhat_client.gaze(FURHAT_AGENT_NAME, {'x':i/10,'y':i/10,'z':2.00})
    #     sleep(0.1)

    furhat_client.say(FURHAT_AGENT_NAME, 'I gazed')
    sleep(0.01)
