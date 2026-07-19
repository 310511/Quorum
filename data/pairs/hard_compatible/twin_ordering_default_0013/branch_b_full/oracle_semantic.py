import unittest
from ordering_013 import first_13

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_13([44, 41]), 41)
