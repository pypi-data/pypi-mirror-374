import os

class ArtifactWriter:
	def __init__(self, run_dir: str = None, base_dir: str = ".", run_id: str = None):
		import os, datetime
		if run_dir is not None:
			self.run_dir = run_dir
		else:
			if run_id is None:
				run_id = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
			self.run_dir = os.path.join(base_dir, "runs", run_id)
		os.makedirs(self.run_dir, exist_ok=True)

	def write_summary(self, session):
		summary_path = os.path.join(self.run_dir, "summary.md")
		with open(summary_path, "w", encoding="utf-8") as f:
			f.write(f"# Summary\n\nSession: {getattr(session, 'app_name', 'unknown')}\n\n")
			f.write("## Flows and Events\n")
			for flow in getattr(session, 'flows', []):
				f.write(f"- **Flow:** {flow.name}\n")
				for event in getattr(flow, 'events', []):
					ev_type = getattr(event, 'event_type', '?')
					step = getattr(event, 'step', '?')
					evidence = getattr(event, 'evidence', None)
					f.write(f"    - [{ev_type}] step: {step}, evidence: {evidence}\n")
			# Summarize failures
			failures = [e for flow in getattr(session, 'flows', []) for e in getattr(flow, 'events', []) if getattr(e, 'event_type', '') == 'failure']
			if failures:
				f.write("\n## Failures\n")
				for fail in failures:
					f.write(f"- step: {getattr(fail, 'step', '?')}, evidence: {getattr(fail, 'evidence', None)}\n")

	def write_ask(self, session):
		ask_path = os.path.join(self.run_dir, "ask.md")
		with open(ask_path, "w", encoding="utf-8") as f:
			f.write(f"# Ask\n\nSession: {getattr(session, 'app_name', 'unknown')}\n\n")
			f.write("## Run Overview\n")
			for flow in getattr(session, 'flows', []):
				f.write(f"- **Flow:** {flow.name}\n")
				for event in getattr(flow, 'events', []):
					ev_type = getattr(event, 'event_type', '?')
					step = getattr(event, 'step', '?')
					evidence = getattr(event, 'evidence', None)
					f.write(f"    - [{ev_type}] step: {step}, evidence: {evidence}\n")
			failures = [e for flow in getattr(session, 'flows', []) for e in getattr(flow, 'events', []) if getattr(e, 'event_type', '') == 'failure']
			if failures:
				f.write("\n## Issues\n")
				for fail in failures:
					f.write(f"- step: {getattr(fail, 'step', '?')}, evidence: {getattr(fail, 'evidence', None)}\n")
			f.write("\n---\nCopilot: Please summarize the run, diagnose failures, and suggest minimal fixes or tests.\n")
