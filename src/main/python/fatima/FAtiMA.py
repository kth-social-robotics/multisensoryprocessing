import sys,os,operator
import clr
from collections import Counter

fatima_lib_path = r"../../fatima/fatima"
fatima_home_path = '../../fatima'
sys.path.append(fatima_lib_path)
clr.AddReference("IntegratedAuthoringTool")

from System import Array
from IntegratedAuthoringTool import IntegratedAuthoringToolAsset
from IntegratedAuthoringTool import IATConsts
from IntegratedAuthoringTool.DTOs import CharacterSourceDTO
from RolePlayCharacter import RolePlayCharacterAsset
from RolePlayCharacter import EventHelper


class DecisionMaking:

	def __init__(self):
		# Load the Scenario Configuration
		self.rpc_file = 'scenarios/werewolf_player.rpc'
		self.outputFile = 'scenarios/output.rpc'

		# Loading the First Character From the Scenario
		self.rpc = RolePlayCharacterAsset.LoadFromFile(os.path.join(fatima_home_path,self.rpc_file))
		self.rpc.LoadAssociatedAssets()

	def action_event(self, a1, a2, a3):
		evt = EventHelper.ActionEnd(a1, a2, a3)
		self.rpc.Perceive(evt)
		self.rpc.SaveToFile(os.path.join(fatima_home_path,self.outputFile))
		self.rpc.Update()

	def property_change(self, a1, a2):
		evt = EventHelper.PropertyChange(a1, a2, 'world')
		self.rpc.Perceive(evt)
		self.rpc.SaveToFile(os.path.join(fatima_home_path,self.outputFile))
		self.rpc.Update()

	def get_accusals(self):
		# toy examples to check that it is actually running
		#self.property_change('GazeMostAt(Blue)', 'Red')
		#self.property_change('GazeMostAt(Red)', 'Blue')
		#self.property_change('IsDead(Blue)', 'false')
		#self.property_change('IsDead(Red)', 'false')
		# getting resulting acts
		accusals = Counter([str(d.Target) for d in self.rpc.Decide()])
		if len(accusals) > 0:
			suspect = max(accusals.items(), key=operator.itemgetter(1))[0].lower()
			probabilities = {key.lower(): float(value) / sum(accusals.values()) for (key, value) in accusals.items()}
			return (suspect, probabilities)
		else:
			return ("No accusals")

	def update_vote(self, player):
		print(player.name,'vote',player.last_vote)
		self.action_event(player.name, "vote", player.last_vote)

	def update_knowledge_base(self, timestep, player):
		self.property_change('is_alive(' + player.name + ')', str(player.is_Alive).lower())
		for attr, value in player.properties.iteritems():
			self.property_change(attr + '('+ player.name + ')', value)
        

        # Examples: Will be replaces by properties of participants
		# self.action_event("White", "vote", "Red")
		# self.property_change('GazeMostAt(Blue)', 'Red')
		# self.property_change('GazeMostAt(Red)', 'Blue')
		# self.property_change('IsDead(Blue)', 'false')
		# self.property_change('IsDead(Red)', 'false')
		# self.property_change('IsDead(White)', 'true')
		# self.property_change('ClosedMouth(Blue)', 'true')
		# self.property_change('EyesOpen(Blue)', 'true')


