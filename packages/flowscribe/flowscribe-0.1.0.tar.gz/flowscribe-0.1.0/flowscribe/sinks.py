import json

class JSONLSink:
	def __init__(self, path):
		self.path = path

	def write(self, event):
		# Try to use to_dict if available, else fallback to __dict__
		if hasattr(event, 'to_dict'):
			data = event.to_dict()
		else:
			data = event.__dict__
		with open(self.path, 'a', encoding='utf-8') as f:
			f.write(json.dumps(data) + '\n')
class ConsoleSink:
	def write(self, event):
		# Print event type in uppercase and event details
		print(f"{event.event_type.upper()}: {event}")
