import unittest
from limits_002 import can_accept_2

class SemanticOracle(unittest.TestCase):
    def test_missing_limit_uses_configured_default(self):
        self.assertTrue(can_accept_2(1))
