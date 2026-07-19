import unittest
from parser_015 import valid_count_15

class SemanticOracle(unittest.TestCase):
    def test_invalid_number_is_rejected(self):
        self.assertFalse(valid_count_15("not-a-number-90"))
