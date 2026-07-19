import unittest
from parser_007 import valid_count_7

class SemanticOracle(unittest.TestCase):
    def test_invalid_number_is_rejected(self):
        self.assertFalse(valid_count_7("not-a-number-42"))
