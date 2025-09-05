import unittest
import os
from flowscribe.artifacts import ArtifactWriter
from flowscribe.core import Session, Event

class TestArtifactWriter(unittest.TestCase):
    def test_write_summary_and_ask(self):
        session = Session(app_name="test", mode="test")
        flow = session.start_flow("test/flow")
        flow.add_event(Event(event_type="failure", flow_id=flow.flow_id, evidence={"err": 1}))
        session.end_session()
        writer = ArtifactWriter(base_dir=".", run_id="testrun")
        writer.write_summary(session)
        writer.write_ask(session)
        self.assertTrue(os.path.exists("./runs/testrun/summary.md"))
        self.assertTrue(os.path.exists("./runs/testrun/ask.md"))
        # Clean up
        import shutil
        shutil.rmtree("./runs/testrun", ignore_errors=True)
