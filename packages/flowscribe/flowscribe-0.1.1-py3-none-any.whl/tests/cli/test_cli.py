import unittest
import subprocess
import sys

class TestCLI(unittest.TestCase):
    def test_cli_entry(self):
        result = subprocess.run([sys.executable, '-m', 'flowscribe.main', 'run', '--app', 'cli-test'], capture_output=True, text=True)
        self.assertIn("Started session", result.stdout)
        self.assertIn("Ended session", result.stdout)
