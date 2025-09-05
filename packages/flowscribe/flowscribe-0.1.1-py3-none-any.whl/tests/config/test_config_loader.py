import unittest
import os
from flowscribe.config import load_config
import yaml

class TestConfigLoader(unittest.TestCase):
    def test_load_and_env_override(self):
        path = "test_ra.yaml"
        with open(path, "w") as f:
            f.write("enabled: false\nprofile: test\n")
        os.environ["RA_ENABLED"] = "1"
        config = load_config(path)
        self.assertTrue(config["enabled"])
        os.remove(path)
        del os.environ["RA_ENABLED"]

    def test_malformed_yaml(self):
        path = "bad.yaml"
        with open(path, "w") as f:
            f.write(": bad yaml")
        with self.assertRaises(Exception):
            load_config(path)
        os.remove(path)
