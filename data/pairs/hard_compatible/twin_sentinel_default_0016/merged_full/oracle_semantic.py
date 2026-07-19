import unittest
from limits_016 import can_accept_16

class SemanticOracle(unittest.TestCase):
    def test_missing_limit_uses_configured_default(self):
        self.assertTrue(can_accept_16(1))
