import unittest
from limits_006 import can_accept_6

class SemanticOracle(unittest.TestCase):
    def test_missing_limit_uses_configured_default(self):
        self.assertTrue(can_accept_6(1))
