import unittest
from ordering_009 import first_9

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_9([32, 29]), 29)
