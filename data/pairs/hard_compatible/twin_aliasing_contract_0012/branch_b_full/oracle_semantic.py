import unittest
from records_012 import without_last_12

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [73, 74, 75]
        without_last_12(values)
        self.assertEqual(values, [73, 74, 75])
