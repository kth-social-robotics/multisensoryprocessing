from furhat import connect_to_iristk

FURHAT_IP = '130.237.67.172' # Furhat IP address
FURHAT_AGENT_NAME = 'system' # Furhat agent name. Can be found under "Connections" in the furhat web-GUI

with connect_to_iristk(FURHAT_IP) as furhat_client:
    def event_callback(event):
        print(event) # Receives each event the furhat sends out.

    furhat_client.start_listening(event_callback) # register our event callback receiver
    furhat_client.say(FURHAT_AGENT_NAME, 'hello humans') # Make furhat say hello
    furhat_client.gaze(FURHAT_AGENT_NAME, {'z':2,'x':0.59,'y':0.76})

    input() # Press enter to quit
