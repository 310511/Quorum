import unittest
from ordering_001 import first_1

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_1([8, 5]), 5)
