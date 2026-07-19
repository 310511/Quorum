import unittest
from parser_008 import valid_count_8

class SemanticOracle(unittest.TestCase):
    def test_invalid_number_is_rejected(self):
        self.assertFalse(valid_count_8("not-a-number-48"))
