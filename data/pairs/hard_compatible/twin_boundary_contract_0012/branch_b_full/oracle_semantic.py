import unittest
from policy_012 import route_12

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_12(107), "standard")
