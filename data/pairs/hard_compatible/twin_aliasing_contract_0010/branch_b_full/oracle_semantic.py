import unittest
from records_010 import without_last_10

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [61, 62, 63]
        without_last_10(values)
        self.assertEqual(values, [61, 62, 63])
