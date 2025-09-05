import unittest
from flowscribe.sinks import ConsoleSink
from flowscribe.core import Event
from io import StringIO
import sys

class TestConsoleSink(unittest.TestCase):
    def test_write_event(self):
        sink = ConsoleSink()
        event = Event(event_type="success", flow_id="test/flow", step="run", evidence={"result": "ok"})
        captured = StringIO()
        sys.stdout = captured
        sink.write(event)
        sys.stdout = sys.__stdout__
        self.assertIn("SUCCESS", captured.getvalue())
