import unittest
from ordering_016 import first_16

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_16([53, 50]), 50)
