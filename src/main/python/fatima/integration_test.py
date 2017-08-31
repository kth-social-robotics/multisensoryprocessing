import sys
import clr

# This variable points to where the FAtiMA Libraries are located in your
# machine
fatima_lib_path = r"C:\GIT\furhat-client-fatima\fatima"
sys.path.append(fatima_lib_path)
clr.AddReference("IntegratedAuthoringTool")

from System import Array
from IntegratedAuthoringTool import IntegratedAuthoringToolAsset
from IntegratedAuthoringTool import IATConsts
from IntegratedAuthoringTool.DTOs import CharacterSourceDTO
from RolePlayCharacter import RolePlayCharacterAsset
from RolePlayCharacter import EventHelper

# Load the Scenario Configuration
scenarioFile = 'C:/GIT/furhat-client-fatima/scenarios/test1.iat'
iat = IntegratedAuthoringToolAsset.LoadFromFile(scenarioFile)
print('- Scenario Information -')
print('Name: ', iat.ScenarioName)
print('Description: ', iat.ScenarioDescription)
print('\n')

# Load All The Character Sources
sources = []
for s in iat.GetAllCharacterSources():
    sources.append(s.Source)

# Loading the First Character From the Scenario
rpc = RolePlayCharacterAsset.LoadFromFile(sources[0])
rpc.LoadAssociatedAssets()
iat.BindToRegistry(rpc.DynamicPropertiesRegistry)

print('- Character Information -')
print('Name: ', rpc.CharacterName)
print('Mood: ', rpc.Mood)
print('\n')

curState = 'Start'
while(curState != 'End'):
    playerDialogs = iat.GetDialogueActionsByState('Player', curState)
    print('- Available Dialogue Options For State: ', curState)
    dialogues = []
    for d in playerDialogs:
        dialogues.append(d)
        print(d.Utterance)
    i = -1
    while(i < 0 or i >= len(dialogues)):
        i = int(input('Select option: '))
    pAct = iat.BuildSpeakActionName('Player', dialogues[i].Id)

    # Action Event
    evt = EventHelper.ActionEnd('Player', str(pAct), str(rpc.CharacterName))
    print('\n', evt, '\n')
    rpc.Perceive(evt)

    # Property Change Event
    curState = dialogues[i].NextState
    dState = 'DialogueState(Player)'
    evt = EventHelper.PropertyChange(dState, curState, 'Player')
    print('\n', evt, '\n')
    rpc.Perceive(evt)

    responses = []
    for d in rpc.Decide():
        pa = []
        for p in d.Parameters:
            pa.append(p)

        for r in iat.GetDialogueActions('Agent', pa[0], pa[1], pa[2], pa[3]):
            responses.append(r)

    response = responses[0]

    print('Character Response: ', responses[0].Utterance)

    # Property Change Event
    curState = responses[0].NextState
    dState = 'DialogueState(Player)'
    evt = EventHelper.PropertyChange(dState, curState, str(rpc.CharacterName))
    print('\n', evt, '\n')
    rpc.Perceive(evt)

    print('\n')
    print('Character Mood: ', rpc.Mood, '\n')
