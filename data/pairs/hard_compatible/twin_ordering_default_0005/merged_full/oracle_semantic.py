import unittest
from ordering_005 import first_5

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_5([20, 17]), 17)
