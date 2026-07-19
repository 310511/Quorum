import unittest
from records_017 import without_last_17

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [103, 104, 105]
        without_last_17(values)
        self.assertEqual(values, [103, 104, 105])
