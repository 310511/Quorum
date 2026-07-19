import unittest
from parser_011 import valid_count_11

class SemanticOracle(unittest.TestCase):
    def test_invalid_number_is_rejected(self):
        self.assertFalse(valid_count_11("not-a-number-66"))
