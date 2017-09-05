import json
import csv
import sys
import yaml
from collections import defaultdict
sys.path.append('../..')
from shared import MessageQueue


# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

class FaceProcessor:
	"""
	An object of FaceProcesser is used to iteratively collect features of
	frames returned by the OpenFace software. Via the function 'collect_frame()'
	one gives frame features one at a time. When it reaches a certain threshold
	it returns higher levels features based on a set of rules for further
	processing.

	"""

	def __init__(self):
		self.frames = []
		self.FRAME_THRESHOLD = 50.0
		self.set_features()

	def update_features(self, frame):
		"""
		Takes a dictionary of OpenFace features of frame as input.
		Updates each high-level feature.
		"""

		if frame['AU45_c']:
			self.blink += 1
		if frame['AU26_c']:# or frame['AU26_c']:
			self.mouth_open += 1
		if frame['AU01_c']:
			self.inner_brow_raise += 1
		if frame['AU02_c']:
			self.outer_brow_raise += 1
		#TODO: Continue building rules

	def collect_frame(self, frame):
		"""
		Collects frames until a certain threshold, it then processes
		the frames, returns high-levels features, and resets values.
		"""

		self.frames.append(frame)
		if len(self.frames) == self.FRAME_THRESHOLD:
			for frame in self.frames:
				self.update_features(frame)
			data = self.get_highlevel_features()
			self.set_features()
			self.frames = []
			return data
		else:
			return False


	def get_highlevel_features(self):
		"""
		Returns processed features, used as input to logic module (FAtiMA).
		"""
		#TODO: Find out optimal format
		data = {}
		data["blink"] = self.blink/self.FRAME_THRESHOLD
		data["mouth_open"] = self.mouth_open/self.FRAME_THRESHOLD
		data["inner_brow_raise"] = self.inner_brow_raise/self.FRAME_THRESHOLD
		data["outer_brow_raise"] = self.outer_brow_raise/self.FRAME_THRESHOLD
		return data

	def set_features(self):
		"""
		Sets or resets features to zero, used after processing of sequence.
		"""
		self.blink = 0
		self.mouth_open = 0
		self.inner_brow_raise = 0
		self.outer_brow_raise = 0
		# TODO: Add highlevel features

participants = defaultdict(FaceProcessor)
def callback(_mq, get_shifted_time, routing_key, body):
	participant = routing_key.rsplit('.', 1)[1]
	data = participants[participant].collect_frame(body)
	if data:
		data["timestamps"] = body["timestamps"]
		_mq.publish(exchange=settings["messaging"]["environment"], routing_key='faceprocessor.{}'.format(participant), body=data)

mq = MessageQueue('face_processor')
mq.bind_queue(
    exchange=settings["messaging"]["pre_processing"], routing_key='openface.data.*', callback=callback
)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
