import unittest
from policy_001 import route_1

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_1(41), "standard")
