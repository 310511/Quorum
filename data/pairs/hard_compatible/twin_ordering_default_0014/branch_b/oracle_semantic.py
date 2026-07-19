import unittest
from ordering_014 import first_14

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_14([47, 44]), 44)
