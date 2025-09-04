import unittest
from flowscribe.privacy import redact_and_limit

class TestPrivacy(unittest.TestCase):
    def test_redact_and_truncate(self):
        data = {"api_key": "SECRET123", "token": "tok", "info": "x"*100}
        redact_keys = ["api_key", "token"]
        payload_limit = 10
        result = redact_and_limit(data, redact_keys, payload_limit)
        self.assertEqual(result["api_key"], "***REDACTED***")
        self.assertEqual(result["token"], "***REDACTED***")
        self.assertTrue(result["info"].startswith("xxxxxxxxxx"))
        self.assertIn("truncated", result["info"])
