import unittest
from policy_014 import route_14

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_14(119), "standard")
