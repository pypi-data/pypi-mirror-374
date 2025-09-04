import os

class ArtifactWriter:
	def __init__(self, base_dir: str = ".", run_id: str = "run"):
		self.base_dir = base_dir
		self.run_id = run_id
		self.run_dir = os.path.join(self.base_dir, "runs", self.run_id)
		os.makedirs(self.run_dir, exist_ok=True)

	def write_summary(self, session):
		summary_path = os.path.join(self.run_dir, "summary.md")
		with open(summary_path, "w", encoding="utf-8") as f:
			f.write("# Summary\n\n")
			f.write(f"Session: {getattr(session, 'app_name', 'unknown')}\n")

	def write_ask(self, session):
		ask_path = os.path.join(self.run_dir, "ask.md")
		with open(ask_path, "w", encoding="utf-8") as f:
			f.write("# Ask\n\n")
			f.write(f"Session: {getattr(session, 'app_name', 'unknown')}\n")
