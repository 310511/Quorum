import unittest
from policy_002 import route_2

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_2(47), "standard")
