import unittest
from parser_004 import valid_count_4

class SemanticOracle(unittest.TestCase):
    def test_invalid_number_is_rejected(self):
        self.assertFalse(valid_count_4("not-a-number-24"))
