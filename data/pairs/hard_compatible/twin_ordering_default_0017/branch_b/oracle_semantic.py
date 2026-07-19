import unittest
from ordering_017 import first_17

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_17([56, 53]), 53)
