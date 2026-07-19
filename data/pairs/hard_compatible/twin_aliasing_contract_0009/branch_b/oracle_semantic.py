import unittest
from records_009 import without_last_9

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [55, 56, 57]
        without_last_9(values)
        self.assertEqual(values, [55, 56, 57])
