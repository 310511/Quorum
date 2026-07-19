import unittest
from policy_008 import route_8

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_8(83), "standard")
