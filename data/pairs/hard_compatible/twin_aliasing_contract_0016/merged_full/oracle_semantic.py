import unittest
from records_016 import without_last_16

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [97, 98, 99]
        without_last_16(values)
        self.assertEqual(values, [97, 98, 99])
