import unittest
from limits_010 import can_accept_10

class SemanticOracle(unittest.TestCase):
    def test_missing_limit_uses_configured_default(self):
        self.assertTrue(can_accept_10(1))
