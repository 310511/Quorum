import unittest
from records_007 import without_last_7

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [43, 44, 45]
        without_last_7(values)
        self.assertEqual(values, [43, 44, 45])
