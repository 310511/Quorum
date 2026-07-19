import unittest
from records_008 import without_last_8

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [49, 50, 51]
        without_last_8(values)
        self.assertEqual(values, [49, 50, 51])
