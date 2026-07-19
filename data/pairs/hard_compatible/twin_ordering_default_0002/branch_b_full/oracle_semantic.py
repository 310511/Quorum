import unittest
from ordering_002 import first_2

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_2([11, 8]), 8)
