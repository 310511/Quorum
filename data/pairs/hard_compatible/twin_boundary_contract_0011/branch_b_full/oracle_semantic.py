import unittest
from policy_011 import route_11

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_11(101), "standard")
