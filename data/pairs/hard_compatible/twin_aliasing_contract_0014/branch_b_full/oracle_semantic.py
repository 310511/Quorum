import unittest
from records_014 import without_last_14

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [85, 86, 87]
        without_last_14(values)
        self.assertEqual(values, [85, 86, 87])
