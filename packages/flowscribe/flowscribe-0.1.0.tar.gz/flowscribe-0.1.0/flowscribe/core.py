from typing import Any, Dict, Optional
import datetime

import uuid

class Flow:
	def __init__(self, flow_id: str, name: str, tags=None):
		self.flow_id = flow_id
		self.name = name
		self.tags = tags if tags is not None else []
		self.events = []

	def add_event(self, event):
		self.events.append(event)

class Session:
	def __init__(self, app_name: str, mode: str = "default", tags=None):
		self.app_name = app_name
		self.mode = mode
		self.tags = tags if tags is not None else []
		self.flows = []
		self.ended = False
		self.end_time = None

	def start_flow(self, name: str, tags=None):
		flow_id = str(uuid.uuid4())
		flow = Flow(flow_id, name, tags=tags)
		self.flows.append(flow)
		return flow

	def end_session(self):
		self.ended = True
		self.end_time = datetime.datetime.utcnow()

	def handle_event(self, event: "Event"):
		# Logic to handle events can be added here
		pass
from typing import Any, Dict, Optional
import datetime

class Event:
	"""
	Represents a single event in the flowscribe system.
	"""
	def __init__(
		self,
		event_type: str,
		flow_id: Optional[str] = None,
		step: Optional[str] = None,
		evidence: Optional[Any] = None,
		data: Optional[Dict[str, Any]] = None,
		timestamp: Optional[datetime.datetime] = None,
	):
		self.event_type = event_type
		self.flow_id = flow_id
		self.step = step
		self.evidence = evidence
		self.data = data or {}
		self.timestamp = timestamp or datetime.datetime.utcnow()

	def to_dict(self) -> Dict[str, Any]:
		return {
			"event_type": self.event_type,
			"flow_id": self.flow_id,
			"step": self.step,
			"evidence": self.evidence,
			"data": self.data,
			"timestamp": self.timestamp.isoformat(),
		}
