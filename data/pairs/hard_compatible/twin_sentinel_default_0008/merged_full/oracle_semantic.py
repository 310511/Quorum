import unittest
from limits_008 import can_accept_8

class SemanticOracle(unittest.TestCase):
    def test_missing_limit_uses_configured_default(self):
        self.assertTrue(can_accept_8(1))
