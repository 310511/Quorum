import unittest
from parser_013 import valid_count_13

class SemanticOracle(unittest.TestCase):
    def test_invalid_number_is_rejected(self):
        self.assertFalse(valid_count_13("not-a-number-78"))
