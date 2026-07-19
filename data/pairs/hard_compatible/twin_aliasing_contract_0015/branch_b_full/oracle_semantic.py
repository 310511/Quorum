import unittest
from records_015 import without_last_15

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [91, 92, 93]
        without_last_15(values)
        self.assertEqual(values, [91, 92, 93])
