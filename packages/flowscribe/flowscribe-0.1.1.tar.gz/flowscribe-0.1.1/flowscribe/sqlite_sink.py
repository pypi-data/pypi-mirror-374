import sqlite3
from typing import Any, Dict, Optional

class SQLiteSink:
	def write(self, event):
		"""
		Accepts an Event object and writes it to the database.
		"""
		if not hasattr(event, 'event_type') or not hasattr(event, 'to_dict'):
			raise ValueError("event must have 'event_type' and 'to_dict' method")
		event_type = event.event_type
		import json
		event_data = json.dumps(event.to_dict())
		self.write_event(event_type, event_data)
	"""
	A sink that writes events to a SQLite database.
	"""
	def __init__(self, db_path: str = None, run_dir: str = None, filename: str = "trace.db"):
		import os
		if run_dir is not None:
			self.db_path = os.path.join(run_dir, filename)
		elif db_path is not None:
			self.db_path = db_path
		else:
			self.db_path = ":memory:"
		self.conn: Optional[sqlite3.Connection] = None
		self._connect()
		self._ensure_table()

	def _connect(self):
		self.conn = sqlite3.connect(self.db_path)

	def _ensure_table(self):
		if self.conn is None:
			raise RuntimeError("No database connection.")
		cur = self.conn.cursor()
		try:
			cur.execute('''
				CREATE TABLE IF NOT EXISTS events (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					event_type TEXT,
					event_data TEXT,
					created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
				)
			''')
			self.conn.commit()
		finally:
			cur.close()

	def write_event(self, event_type: str, event_data: str):
		if self.conn is None:
			raise RuntimeError("No database connection.")
		cur = self.conn.cursor()
		try:
			cur.execute(
				"INSERT INTO events (event_type, event_data) VALUES (?, ?)",
				(event_type, event_data)
			)
			self.conn.commit()
		finally:
			cur.close()

	def close(self):
		if self.conn:
			self.conn.close()
			self.conn = None
			# Help release file handle on Windows
			import gc
			gc.collect()
