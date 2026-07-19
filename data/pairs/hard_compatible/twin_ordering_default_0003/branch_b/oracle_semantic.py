import unittest
from ordering_003 import first_3

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_3([14, 11]), 11)
