import unittest
from policy_017 import route_17

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_17(137), "standard")
