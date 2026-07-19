import unittest
from policy_015 import route_15

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_15(125), "standard")
