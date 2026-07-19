import unittest
from policy_013 import route_13

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_13(113), "standard")
