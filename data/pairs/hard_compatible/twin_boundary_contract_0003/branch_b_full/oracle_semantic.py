import unittest
from policy_003 import route_3

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_3(53), "standard")
