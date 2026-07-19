import unittest
from ordering_015 import first_15

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_15([50, 47]), 47)
