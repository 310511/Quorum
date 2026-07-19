import unittest
from records_005 import without_last_5

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [31, 32, 33]
        without_last_5(values)
        self.assertEqual(values, [31, 32, 33])
