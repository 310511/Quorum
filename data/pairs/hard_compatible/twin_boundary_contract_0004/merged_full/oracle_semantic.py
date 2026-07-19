import unittest
from policy_004 import route_4

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_4(59), "standard")
