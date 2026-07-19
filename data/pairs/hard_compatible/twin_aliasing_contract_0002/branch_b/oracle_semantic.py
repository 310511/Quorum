import unittest
from records_002 import without_last_2

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [13, 14, 15]
        without_last_2(values)
        self.assertEqual(values, [13, 14, 15])
