import unittest
from records_001 import without_last_1

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [7, 8, 9]
        without_last_1(values)
        self.assertEqual(values, [7, 8, 9])
