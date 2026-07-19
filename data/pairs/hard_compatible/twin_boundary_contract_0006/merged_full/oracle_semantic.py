import unittest
from policy_006 import route_6

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_6(71), "standard")
