import unittest
from ordering_012 import first_12

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_12([41, 38]), 38)
