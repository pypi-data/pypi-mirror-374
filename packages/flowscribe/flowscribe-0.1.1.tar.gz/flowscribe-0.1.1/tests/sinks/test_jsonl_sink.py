import unittest
import os
from flowscribe.sinks import JSONLSink
from flowscribe.core import Event

class TestJSONLSink(unittest.TestCase):
    def test_write_event(self):
        path = "test_trace.jsonl"
        if os.path.exists(path):
            os.remove(path)
        sink = JSONLSink(path)
        event = Event(event_type="failure", flow_id="test/flow", step="fail", evidence={"error": "bad"})
        sink.write(event)
        with open(path) as f:
            line = f.readline()
            self.assertIn('"failure"', line)
        os.remove(path)
