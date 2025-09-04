"""
Example: Using Flowscribe for a simple data processing flow
"""
from flowscribe.core import Session, Event
from flowscribe.sinks import ConsoleSink, JSONLSink
from flowscribe.artifacts import ArtifactWriter
import random

# Set up session and sinks
session = Session(app_name="example-app", mode="demo", tags=["example"])
console_sink = ConsoleSink()
jsonl_sink = JSONLSink("example_trace.jsonl")

# Start a flow
flow = session.start_flow("data/processing", tags=["etl"])

# Simulate steps in the flow
for i in range(3):
    step_name = f"step_{i+1}"
    # Simulate success/failure
    if random.random() > 0.2:
        event = Event(event_type="success", flow_id=flow.flow_id, step=step_name, evidence={"row": i})
    else:
        event = Event(event_type="failure", flow_id=flow.flow_id, step=step_name, evidence={"row": i, "error": "Simulated error"})
    flow.add_event(event)
    console_sink.write(event)
    jsonl_sink.write(event)

# End session
session.end_session()

# Write artifacts
writer = ArtifactWriter(base_dir=".", run_id="example_run")
writer.write_summary(session)
writer.write_ask(session)

print("\nArtifacts written to ./runs/example_run/")
print("Trace written to example_trace.jsonl")
