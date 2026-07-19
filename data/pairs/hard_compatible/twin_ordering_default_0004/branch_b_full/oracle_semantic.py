import unittest
from ordering_004 import first_4

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_4([17, 14]), 14)
