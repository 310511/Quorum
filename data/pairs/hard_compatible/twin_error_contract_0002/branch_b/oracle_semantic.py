import unittest
from parser_002 import valid_count_2

class SemanticOracle(unittest.TestCase):
    def test_invalid_number_is_rejected(self):
        self.assertFalse(valid_count_2("not-a-number-12"))
