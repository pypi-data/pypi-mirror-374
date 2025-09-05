"""
Test flows for flowscribe core functionality.
"""
import unittest
from flowscribe.core import Session, Event

class TestFlowscribe(unittest.TestCase):
    def test_basic_flow(self):
        session = Session(app_name="test-app", mode="test", tags=["unit"])
        flow = session.start_flow("test/flow", tags=["demo"])
        event = Event(event_type="checkpoint", flow_id=flow.flow_id, step="start", evidence={"count": 1})
        flow.add_event(event)
        session.end_session()
        self.assertEqual(flow.events[0].event_type, "checkpoint")
        self.assertIsNotNone(session.end_time)

if __name__ == "__main__":
    unittest.main()
