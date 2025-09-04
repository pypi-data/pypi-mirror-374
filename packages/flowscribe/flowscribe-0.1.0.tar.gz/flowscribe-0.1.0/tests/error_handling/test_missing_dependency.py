import unittest
from unittest.mock import patch
import sys

class TestMissingDependency(unittest.TestCase):
    def test_missing_pyyaml(self):
        with patch.dict('sys.modules', {'yaml': None}):
            from flowscribe.config import load_config
            with self.assertRaises(ImportError):
                load_config('dummy.yaml')
