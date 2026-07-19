import unittest
from ordering_008 import first_8

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_8([29, 26]), 26)
