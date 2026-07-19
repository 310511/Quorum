import unittest
from records_004 import without_last_4

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [25, 26, 27]
        without_last_4(values)
        self.assertEqual(values, [25, 26, 27])
