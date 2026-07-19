import unittest
from ordering_011 import first_11

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_11([38, 35]), 35)
