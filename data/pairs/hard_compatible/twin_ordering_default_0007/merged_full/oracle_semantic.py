import unittest
from ordering_007 import first_7

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_7([26, 23]), 23)
