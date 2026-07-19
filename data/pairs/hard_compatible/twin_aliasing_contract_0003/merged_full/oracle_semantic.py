import unittest
from records_003 import without_last_3

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [19, 20, 21]
        without_last_3(values)
        self.assertEqual(values, [19, 20, 21])
