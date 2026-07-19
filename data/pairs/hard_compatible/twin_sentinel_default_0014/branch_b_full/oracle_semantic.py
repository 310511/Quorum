import unittest
from limits_014 import can_accept_14

class SemanticOracle(unittest.TestCase):
    def test_missing_limit_uses_configured_default(self):
        self.assertTrue(can_accept_14(1))
