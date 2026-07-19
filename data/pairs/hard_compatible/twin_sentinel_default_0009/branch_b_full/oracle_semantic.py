import unittest
from limits_009 import can_accept_9

class SemanticOracle(unittest.TestCase):
    def test_missing_limit_uses_configured_default(self):
        self.assertTrue(can_accept_9(1))
