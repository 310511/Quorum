import unittest
from policy_005 import route_5

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_5(65), "standard")
