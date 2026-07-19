import unittest
from ordering_006 import first_6

class SemanticOracle(unittest.TestCase):
    def test_first_means_smallest(self):
        self.assertEqual(first_6([23, 20]), 20)
