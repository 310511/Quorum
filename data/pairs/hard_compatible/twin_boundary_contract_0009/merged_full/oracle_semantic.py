import unittest
from policy_009 import route_9

class SemanticOracle(unittest.TestCase):
    def test_boundary_remains_standard(self):
        self.assertEqual(route_9(89), "standard")
