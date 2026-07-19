import unittest
from records_011 import without_last_11

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [67, 68, 69]
        without_last_11(values)
        self.assertEqual(values, [67, 68, 69])
