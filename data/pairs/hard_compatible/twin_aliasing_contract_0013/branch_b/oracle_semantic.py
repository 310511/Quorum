import unittest
from records_013 import without_last_13

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [79, 80, 81]
        without_last_13(values)
        self.assertEqual(values, [79, 80, 81])
