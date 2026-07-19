import unittest
from records_006 import without_last_6

class SemanticOracle(unittest.TestCase):
    def test_input_is_not_mutated(self):
        values = [37, 38, 39]
        without_last_6(values)
        self.assertEqual(values, [37, 38, 39])
