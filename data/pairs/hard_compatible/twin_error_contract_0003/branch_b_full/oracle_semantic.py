import unittest
from parser_003 import valid_count_3

class SemanticOracle(unittest.TestCase):
    def test_invalid_number_is_rejected(self):
        self.assertFalse(valid_count_3("not-a-number-18"))
