import unittest
from policy_016 import route_16

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_16(131), "standard")
