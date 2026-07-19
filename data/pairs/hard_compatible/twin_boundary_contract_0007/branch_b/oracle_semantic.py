import unittest
from policy_007 import route_7

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_7(77), "standard")
