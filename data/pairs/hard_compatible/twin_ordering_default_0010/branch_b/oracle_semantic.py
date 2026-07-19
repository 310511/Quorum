import unittest
from ordering_010 import first_10

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_10([35, 32]), 32)
