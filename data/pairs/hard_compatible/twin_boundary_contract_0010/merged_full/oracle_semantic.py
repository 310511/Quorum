import unittest
from policy_010 import route_10

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_10(95), "standard")
