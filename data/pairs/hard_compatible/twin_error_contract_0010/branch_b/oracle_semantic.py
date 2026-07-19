import unittest
from parser_010 import valid_count_10

class SemanticOracle(unittest.TestCase):
    def test_invalid_number_is_rejected(self):
        self.assertFalse(valid_count_10("not-a-number-60"))
